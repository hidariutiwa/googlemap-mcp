from argparse import ArgumentParser
from typing import List

from fastmcp import FastMCP

from googlemap_mcp.tools.geocoding import GeocodingClient
from googlemap_mcp.tools.places import PlacesClient
from googlemap_mcp.tools.routes import RoutesClient

mcp = FastMCP("GoogleMaps MCP")


def run() -> None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument("apikey", help="Google Maps API_KEY")
    args = arg_parser.parse_args()
    api_key = args.apikey

    routes_client = RoutesClient(api_key=api_key)
    places_client = PlacesClient(api_key=api_key)
    geocoding_client = GeocodingClient(api_key=api_key)

    @mcp.tool()
    def compute_routes(
        origin: dict,
        destination: dict,
        travel_mode: str = "DRIVE",
        language_code: str = "ja",
        field_mask: List[str] = [
            "routes.duration",
            "routes.distanceMeters",
            "routes.polyline.encodedPolyline",
        ],
    ) -> dict:
        """2地点間のルートを計算します。origin と destination に緯度経度を指定し、移動手段（DRIVE, WALK, BICYCLE, TRANSIT）を選択できます。"""
        return routes_client.compute_routes(
            origin=origin,
            destination=destination,
            travel_mode=travel_mode,
            language_code=language_code,
            field_mask=field_mask,
        )

    @mcp.tool()
    def compute_route_matrix(
        origins: List[dict],
        destinations: List[dict],
        travel_mode: str = "DRIVE",
        field_mask: List[str] = [
            "originIndex",
            "destinationIndex",
            "duration",
            "distanceMeters",
            "status",
            "condition",
        ],
    ) -> dict:
        """複数の出発地と目的地の間の距離・所要時間マトリクスを計算します。"""
        return routes_client.compute_route_matrix(
            origins=origins,
            destinations=destinations,
            travel_mode=travel_mode,
            field_mask=field_mask,
        )

    @mcp.tool()
    def text_search(
        text_query: str,
        language_code: str = "ja",
        field_mask: List[str] = [
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
        ],
    ) -> dict:
        """テキストクエリで場所を検索します。店名や施設名などのキーワードで検索できます。"""
        return places_client.text_search(
            text_query=text_query,
            language_code=language_code,
            field_mask=field_mask,
        )

    @mcp.tool()
    def nearby_search(
        latitude: float,
        longitude: float,
        radius: float = 500.0,
        included_types: List[str] = [],
        language_code: str = "ja",
        max_result_count: int = 10,
        field_mask: List[str] = [
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
            "places.types",
        ],
    ) -> dict:
        """指定した座標の周辺にある場所を検索します。半径やタイプで絞り込みが可能です。"""
        return places_client.nearby_search(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            included_types=included_types,
            language_code=language_code,
            max_result_count=max_result_count,
            field_mask=field_mask,
        )

    @mcp.tool()
    def geocode(
        address: str,
        language: str = "ja",
    ) -> dict:
        """住所から座標（緯度・経度）を取得します。"""
        return geocoding_client.geocode(
            address=address,
            language=language,
        )

    @mcp.tool()
    def reverse_geocode(
        latitude: float,
        longitude: float,
        language: str = "ja",
    ) -> dict:
        """座標（緯度・経度）から住所を取得します。"""
        return geocoding_client.reverse_geocode(
            latitude=latitude,
            longitude=longitude,
            language=language,
        )

    mcp.run()
