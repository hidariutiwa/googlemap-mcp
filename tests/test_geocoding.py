from unittest.mock import MagicMock, patch

import pytest

from googlemap_mcp.tools.geocoding import GeocodingClient

API_KEY = "test-api-key"


@pytest.fixture
def client():
    return GeocodingClient(api_key=API_KEY)


def _mock_httpx_client(mock_client_cls, response_json, status_code=200):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_response = MagicMock()
    mock_response.json.return_value = response_json
    mock_response.status_code = status_code
    mock_client.get.return_value = mock_response
    return mock_client


class TestGeocode:
    def test_normal(self, client):
        expected = {
            "results": [
                {
                    "formatted_address": "日本、〒105-0011 東京都港区芝公園４丁目２−８",
                    "geometry": {
                        "location": {"lat": 35.6585805, "lng": 139.7454329}
                    },
                }
            ],
            "status": "OK",
        }

        with patch("googlemap_mcp.tools.geocoding.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.geocode("東京タワー")

        assert result == expected
        mock.get.assert_called_once()
        call_kwargs = mock.get.call_args
        assert call_kwargs.kwargs["url"] == "https://maps.googleapis.com/maps/api/geocode/json"
        assert call_kwargs.kwargs["params"]["address"] == "東京タワー"
        assert call_kwargs.kwargs["params"]["language"] == "ja"
        assert call_kwargs.kwargs["params"]["key"] == API_KEY

    def test_custom_params(self, client):
        expected = {"results": [], "status": "OK"}

        with patch("googlemap_mcp.tools.geocoding.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.geocode("Tokyo Tower", language="en")

        assert result == expected
        call_kwargs = mock.get.call_args
        assert call_kwargs.kwargs["params"]["address"] == "Tokyo Tower"
        assert call_kwargs.kwargs["params"]["language"] == "en"
        assert call_kwargs.kwargs["params"]["key"] == API_KEY

    def test_error_returns_none(self, client):
        with patch("googlemap_mcp.tools.geocoding.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = Exception("API error")
            result = client.geocode("東京タワー")

        assert result is None


class TestReverseGeocode:
    def test_normal(self, client):
        expected = {
            "results": [
                {
                    "formatted_address": "日本、〒100-0001 東京都千代田区千代田１−１",
                }
            ],
            "status": "OK",
        }

        with patch("googlemap_mcp.tools.geocoding.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.reverse_geocode(35.6812, 139.7671)

        assert result == expected
        mock.get.assert_called_once()
        call_kwargs = mock.get.call_args
        assert call_kwargs.kwargs["url"] == "https://maps.googleapis.com/maps/api/geocode/json"
        assert call_kwargs.kwargs["params"]["latlng"] == "35.6812,139.7671"
        assert call_kwargs.kwargs["params"]["language"] == "ja"
        assert call_kwargs.kwargs["params"]["key"] == API_KEY

    def test_custom_params(self, client):
        expected = {"results": [], "status": "OK"}

        with patch("googlemap_mcp.tools.geocoding.httpx.Client") as mock_cls:
            mock = _mock_httpx_client(mock_cls, expected)
            result = client.reverse_geocode(35.6812, 139.7671, language="en")

        assert result == expected
        call_kwargs = mock.get.call_args
        assert call_kwargs.kwargs["params"]["latlng"] == "35.6812,139.7671"
        assert call_kwargs.kwargs["params"]["language"] == "en"
        assert call_kwargs.kwargs["params"]["key"] == API_KEY

    def test_error_returns_none(self, client):
        with patch("googlemap_mcp.tools.geocoding.httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = Exception("Network error")
            result = client.reverse_geocode(35.6812, 139.7671)

        assert result is None
