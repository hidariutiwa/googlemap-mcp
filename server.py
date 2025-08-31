import os
import asyncio
from dotenv import load_dotenv

from google.type import latlng_pb2
from google.protobuf.json_format import MessageToJson
from google.maps import places_v1

from mcp.server.fastmcp import FastMCP


load_dotenv()
api_key = os.getenv("GOOGLEMAPS_API_KEY")
if not api_key:
    raise ValueError("GOOGLEMAPS_API_KEY not found in environment variables.")


mcp = FastMCP("googlemap-mcp")


@mcp.tool()
async def text_search(text_query: str) -> str:
    """
    Perform a text search for places using the Google Maps Places API.
    example of text_query: "東京都新宿区 銭湯"
    """
    client = places_v1.PlacesAsyncClient(client_options={"api_key": api_key})
    # Build the request
    request = places_v1.SearchTextRequest(
        text_query=text_query,
        open_now=True,
        price_levels=[
            places_v1.types.PriceLevel.PRICE_LEVEL_MODERATE,
            places_v1.types.PriceLevel.PRICE_LEVEL_EXPENSIVE
        ]
    )
    # Set the field mask
    fieldMask = "places.id,places.displayName,places.primaryTypeDisplayName,places.primaryType,places.rating,places.userRatingCount,places.reviewSummary,places.shortFormattedAddress,places.formattedAddress,places.location,places.currentOpeningHours,places.regularOpeningHours,places.googleMapsUri,places.websiteUri,places.priceRange"
    # Make the request
    try:
        response = await client.search_text(
            request=request,
            metadata=[("x-goog-fieldmask", fieldMask)]
        )

        json_str = MessageToJson(
            response._pb,
            indent=2,
            ensure_ascii=False,
        )
        return json_str
    except Exception as e:
        return f"An error occurred: {e}"


@mcp.tool()
async def nearby_search(lat: float, lng: float, radius_meters: float = 10000.0) -> str:
    """
    Perform a nearby search for places using the Google Maps Places API.
    example of lat,lng: 35.6938403,139.7035496
    radius_meters: search radius in meters (default: 10000.0)
    10,000 meters = 10 kilometers
    """
    # Create the LatLng object for the center
    center_point = latlng_pb2.LatLng(latitude=lat, longitude=lng)
    # Create the circle
    circle_area = places_v1.types.Circle(
        center=center_point,
        radius=radius_meters
    )
    # Add the circle to the location restriction
    location_restriction = places_v1.SearchNearbyRequest.LocationRestriction(
        circle=circle_area
    )
    client = places_v1.PlacesAsyncClient(client_options={"api_key": api_key})
    # Build the request
    request = places_v1.SearchNearbyRequest(
        location_restriction=location_restriction,
        included_types=["restaurant"],
        max_result_count=20,
        language_code="ja",
    )
    # Set the field mask
    # fieldMask = "places.id,places.displayName,places.primaryTypeDisplayName,places.primaryType,places.rating,places.userRatingCount,places.reviewSummary,places.shortFormattedAddress,places.formattedAddress,places.location,places.currentOpeningHours,places.regularOpeningHours,places.googleMapsUri,places.websiteUri,places.priceRange"
    fieldMask = "places.formattedAddress,places.displayName"
    # Make the request
    try:
        response = await client.search_nearby(
            request=request,
            metadata=[("x-goog-fieldmask", fieldMask)]
        )
        json_str = MessageToJson(
            response._pb,
            indent=2,
            ensure_ascii=False,
        )
        return json_str
    except Exception as e:
        raise e


def main():
    mcp.run()


async def test():
    # 新宿駅
    # text_search_result = await text_search("東京都新宿区 銭湯")
    # print(text_search_result)

    # 35.6938403,139.7035496
    nearby_search_result = await nearby_search(35.6938403, 139.7035496, 10000.0)
    print(nearby_search_result)


if __name__ == "__main__":
    # main()
    # 新宿駅
    asyncio.run(test())
