from pydantic import BaseModel, Field
from typing import List

import httpx


class PlacesClient(BaseModel):
    api_key: str = Field(...)

    def text_search(
        self,
        text_query: str,
        language_code: str = "ja",
        field_mask: List[str] = [
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
        ],
    ) -> dict | None:
        try:
            _field_mask = ",".join(field_mask)
            headers = {
                "X-Goog-Api-Key": self.api_key,
                "Content-Type": "application/json",
                "X-Goog-FieldMask": _field_mask,
            }
            data = {"textQuery": text_query, "languageCode": language_code}

            with httpx.Client() as client:
                response = client.post(
                    url="https://places.googleapis.com/v1/places:searchText",
                    headers=headers,
                    json=data,
                )
                print(f"status: {response.status_code}")
                print(f"data: {response.json()}")
                return response.json()
        except Exception as e:
            print(e)
            return None

    def nearby_search(
        self,
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
    ) -> dict | None:
        try:
            _field_mask = ",".join(field_mask)
            headers = {
                "X-Goog-Api-Key": self.api_key,
                "Content-Type": "application/json",
                "X-Goog-FieldMask": _field_mask,
            }
            data = {
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": latitude, "longitude": longitude},
                        "radius": radius,
                    }
                },
                "includedTypes": included_types,
                "languageCode": language_code,
                "maxResultCount": max_result_count,
            }

            with httpx.Client() as client:
                response = client.post(
                    url="https://places.googleapis.com/v1/places:searchNearby",
                    headers=headers,
                    json=data,
                )
                print(f"status: {response.status_code}")
                print(f"data: {response.json()}")
                return response.json()
        except Exception as e:
            print(e)
            return None
