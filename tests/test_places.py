from unittest.mock import MagicMock, patch

import pytest

from googlemap_mcp.tools.places import PlacesClient

API_KEY = "test-api-key"


@pytest.fixture
def client():
    return PlacesClient(api_key=API_KEY)


def _mock_httpx_client(mock_client_cls, response_json, status_code=200):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_response = MagicMock()
    mock_response.json.return_value = response_json
    mock_response.status_code = status_code
    mock_client.post.return_value = mock_response
    return mock_client


class TestTextSearch:
    def test_normal(self, client):
        expected = {
            "places": [
                {
                    "id": "place_123",
                    "displayName": {"text": "東京タワー"},
                    "formattedAddress": "東京都港区芝公園4丁目2-8",
                    "location": {"latitude": 35.6586, "longitude": 139.7454},
                }
            ]
        }

        with patch("googlemap_mcp.tools.places.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.text_search("東京タワー")

        assert result == expected
        mock.post.assert_called_once()
        call_kwargs = mock.post.call_args
        assert call_kwargs.kwargs["url"] == "https://places.googleapis.com/v1/places:searchText"
        assert call_kwargs.kwargs["headers"]["X-Goog-Api-Key"] == API_KEY
        assert call_kwargs.kwargs["headers"]["X-Goog-FieldMask"] == "places.id,places.displayName,places.formattedAddress,places.location"
        body = call_kwargs.kwargs["json"]
        assert body["textQuery"] == "東京タワー"
        assert body["languageCode"] == "ja"

    def test_custom_params(self, client):
        expected = {"places": [{"id": "place_456"}]}

        with patch("googlemap_mcp.tools.places.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.text_search(
                "Tokyo Tower",
                language_code="en",
                field_mask=["places.id"],
            )

        assert result == expected
        call_kwargs = mock.post.call_args
        assert call_kwargs.kwargs["json"]["textQuery"] == "Tokyo Tower"
        assert call_kwargs.kwargs["json"]["languageCode"] == "en"
        assert call_kwargs.kwargs["headers"]["X-Goog-FieldMask"] == "places.id"

    def test_error_returns_none(self, client):
        with patch("googlemap_mcp.tools.places.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = Exception("API error")
            result = client.text_search("test")

        assert result is None


class TestNearbySearch:
    def test_normal(self, client):
        expected = {
            "places": [
                {
                    "id": "place_789",
                    "displayName": {"text": "東京駅"},
                    "formattedAddress": "東京都千代田区丸の内1丁目",
                    "location": {"latitude": 35.6812, "longitude": 139.7671},
                    "types": ["train_station"],
                }
            ]
        }

        with patch("googlemap_mcp.tools.places.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.nearby_search(latitude=35.6812, longitude=139.7671)

        assert result == expected
        mock.post.assert_called_once()
        call_kwargs = mock.post.call_args
        assert call_kwargs.kwargs["url"] == "https://places.googleapis.com/v1/places:searchNearby"
        assert call_kwargs.kwargs["headers"]["X-Goog-Api-Key"] == API_KEY
        assert call_kwargs.kwargs["headers"]["X-Goog-FieldMask"] == "places.id,places.displayName,places.formattedAddress,places.location,places.types"
        body = call_kwargs.kwargs["json"]
        assert body["locationRestriction"]["circle"]["center"]["latitude"] == 35.6812
        assert body["locationRestriction"]["circle"]["center"]["longitude"] == 139.7671
        assert body["locationRestriction"]["circle"]["radius"] == 500.0
        assert body["languageCode"] == "ja"
        assert body["maxResultCount"] == 10

    def test_with_types(self, client):
        expected = {"places": [{"id": "place_rest"}]}

        with patch("googlemap_mcp.tools.places.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.nearby_search(
                latitude=35.6812,
                longitude=139.7671,
                included_types=["restaurant"],
            )

        assert result == expected
        call_kwargs = mock.post.call_args
        assert call_kwargs.kwargs["json"]["includedTypes"] == ["restaurant"]

    def test_custom_params(self, client):
        expected = {"places": [{"id": "place_custom"}]}

        with patch("googlemap_mcp.tools.places.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.nearby_search(
                latitude=34.6937,
                longitude=135.5023,
                radius=1000.0,
                max_result_count=5,
                language_code="en",
            )

        assert result == expected
        call_kwargs = mock.post.call_args
        body = call_kwargs.kwargs["json"]
        assert body["locationRestriction"]["circle"]["radius"] == 1000.0
        assert body["maxResultCount"] == 5
        assert body["languageCode"] == "en"

    def test_error_returns_none(self, client):
        with patch("googlemap_mcp.tools.places.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = Exception("API error")
            result = client.nearby_search(latitude=35.6812, longitude=139.7671)

        assert result is None
