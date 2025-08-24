import os
import asyncio
from dotenv import load_dotenv

from google.maps import places_v1
from google.type import latlng_pb2
from google.protobuf.json_format import MessageToJson

load_dotenv()
api_key = os.getenv("GOOGLEMAPS_API_KEY")
if not api_key:
    raise ValueError("GOOGLEMAPS_API_KEY not found in environment variables.")


async def text_search(text_query: str) -> str:
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


async def main():
    result = await text_search("東京都府中市 焼肉")
    print(result)
    with open("output.json", "w", encoding="utf-8") as f:
        f.write(result)

if __name__ == "__main__":
    asyncio.run(main())
