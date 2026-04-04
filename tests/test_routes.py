from unittest.mock import MagicMock, patch

import pytest

from googlemap_mcp.tools.routes import RoutesClient

API_KEY = "test-api-key"


@pytest.fixture
def client():
    return RoutesClient(api_key=API_KEY)


@pytest.fixture
def origin():
    return {"latitude": 35.6812, "longitude": 139.7671}


@pytest.fixture
def destination():
    return {"latitude": 35.6586, "longitude": 139.7454}


def _mock_httpx_client(mock_client_cls, response_json, status_code=200):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_response = MagicMock()
    mock_response.json.return_value = response_json
    mock_response.status_code = status_code
    mock_client.post.return_value = mock_response
    return mock_client


class TestComputeRoutes:
    def test_normal(self, client, origin, destination):
        expected = {
            "routes": [
                {
                    "duration": "600s",
                    "distanceMeters": 3000,
                    "polyline": {"encodedPolyline": "abc123"},
                }
            ]
        }

        with patch("googlemap_mcp.tools.routes.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.compute_routes(origin, destination)

        assert result == expected
        mock.post.assert_called_once()
        call_kwargs = mock.post.call_args
        assert call_kwargs.kwargs["url"] == "https://routes.googleapis.com/directions/v2:computeRoutes"
        assert call_kwargs.kwargs["headers"]["X-Goog-Api-Key"] == API_KEY
        assert call_kwargs.kwargs["headers"]["X-Goog-FieldMask"] == "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        body = call_kwargs.kwargs["json"]
        assert body["origin"]["location"]["latLng"]["latitude"] == origin["latitude"]
        assert body["destination"]["location"]["latLng"]["latitude"] == destination["latitude"]
        assert body["travelMode"] == "DRIVE"
        assert body["languageCode"] == "ja"

    def test_custom_params(self, client, origin, destination):
        expected = {"routes": [{"duration": "300s"}]}

        with patch("googlemap_mcp.tools.routes.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.compute_routes(
                origin,
                destination,
                travel_mode="WALK",
                language_code="en",
                field_mask=["routes.duration"],
            )

        assert result == expected
        call_kwargs = mock.post.call_args
        assert call_kwargs.kwargs["json"]["travelMode"] == "WALK"
        assert call_kwargs.kwargs["json"]["languageCode"] == "en"
        assert call_kwargs.kwargs["headers"]["X-Goog-FieldMask"] == "routes.duration"

    def test_error_returns_none(self, client, origin, destination):
        with patch("googlemap_mcp.tools.routes.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = Exception("API error")
            result = client.compute_routes(origin, destination)

        assert result is None


class TestComputeRouteMatrix:
    @pytest.fixture
    def origins(self):
        return [
            {"latitude": 35.6812, "longitude": 139.7671},
            {"latitude": 35.6586, "longitude": 139.7454},
        ]

    @pytest.fixture
    def destinations(self):
        return [
            {"latitude": 34.6937, "longitude": 135.5023},
            {"latitude": 35.0116, "longitude": 135.7681},
        ]

    def test_normal(self, client, origins, destinations):
        expected = [
            {
                "originIndex": 0,
                "destinationIndex": 0,
                "duration": "18000s",
                "distanceMeters": 500000,
                "status": {},
                "condition": "ROUTE_EXISTS",
            }
        ]

        with patch("googlemap_mcp.tools.routes.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.compute_route_matrix(origins, destinations)

        assert result == expected
        mock.post.assert_called_once()
        call_kwargs = mock.post.call_args
        assert call_kwargs.kwargs["url"] == "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
        assert call_kwargs.kwargs["headers"]["X-Goog-Api-Key"] == API_KEY
        body = call_kwargs.kwargs["json"]
        assert len(body["origins"]) == 2
        assert len(body["destinations"]) == 2
        assert body["origins"][0]["waypoint"]["location"]["latLng"]["latitude"] == 35.6812
        assert body["travelMode"] == "DRIVE"

    def test_custom_params(self, client, origins, destinations):
        expected = [{"originIndex": 0, "destinationIndex": 0}]

        with patch("googlemap_mcp.tools.routes.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.compute_route_matrix(
                origins,
                destinations,
                travel_mode="BICYCLE",
                field_mask=["originIndex", "destinationIndex"],
            )

        assert result == expected
        call_kwargs = mock.post.call_args
        assert call_kwargs.kwargs["json"]["travelMode"] == "BICYCLE"
        assert call_kwargs.kwargs["headers"]["X-Goog-FieldMask"] == "originIndex,destinationIndex"

    def test_error_returns_none(self, client):
        with patch("googlemap_mcp.tools.routes.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = Exception("Network error")
            result = client.compute_route_matrix(
                [{"latitude": 0, "longitude": 0}],
                [{"latitude": 1, "longitude": 1}],
            )

        assert result is None
