import os
import asyncio
from dotenv import load_dotenv

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
        response = await client.search_text(request=request, metadata=[("x-goog-fieldmask", fieldMask)])

        json_str = MessageToJson(
            response._pb,
            indent=2,
            ensure_ascii=False,
        )
        return json_str
    except Exception as e:
        return f"An error occurred: {e}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
