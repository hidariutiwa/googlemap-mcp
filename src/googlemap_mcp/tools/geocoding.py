from pydantic import BaseModel, Field

import httpx


class GeocodingClient(BaseModel):
    api_key: str = Field(...)

    def geocode(
        self,
        address: str,
        language: str = "ja",
    ) -> dict | None:
        try:
            with httpx.Client() as client:
                response = client.get(
                    url="https://maps.googleapis.com/maps/api/geocode/json",
                    params={
                        "address": address,
                        "language": language,
                        "key": self.api_key,
                    },
                )
                print(f"status: {response.status_code}")
                print(f"data: {response.json()}")
                return response.json()
        except Exception as e:
            print(e)

    def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
        language: str = "ja",
    ) -> dict | None:
        try:
            with httpx.Client() as client:
                response = client.get(
                    url="https://maps.googleapis.com/maps/api/geocode/json",
                    params={
                        "latlng": f"{latitude},{longitude}",
                        "language": language,
                        "key": self.api_key,
                    },
                )
                print(f"status: {response.status_code}")
                print(f"data: {response.json()}")
                return response.json()
        except Exception as e:
            print(e)
