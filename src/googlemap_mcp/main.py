from argparse import ArgumentParser
from typing import List

from fastmcp import FastMCP

from googlemap_mcp.tools.places import PlacesClient
from googlemap_mcp.tools.routes import RoutesClient

mcp = FastMCP("GoogleMaps MCP")


def run() -> None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument("apikey", help="Google Maps API_KEY")
    args = arg_parser.parse_args()
    aei_key = args.apikey

    routes_client = RoutesClient(api_key=aei_key)

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

    mcp.run()
