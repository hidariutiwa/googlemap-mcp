from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, List
from enum import Enum

import httpx


class PlacesFiealdMask(Enum):
    pass


class TextSearchBody(BaseModel):
    text_query: str = Field(...)


class TextSearchRequest(BaseModel):
    body: TextSearchBody = Field(...)
    field_mask: List[str] = Field(
        default=[
            "places.attributions",
            "places.id",
            "places.name",
            "places.displayName",
            "places.photos",
        ]
    )


class PlacesClient(BaseModel):
    api_key: str = Field(...)
    __base_url: str = PrivateAttr()

    def model_post_init(self, __context):
        pass

    def text_search(
        self,
        text_query: str,
        field_mask: List[str] = [
            "places.attributions",
            "places.id",
            "places.name",
            "places.displayName",
            "places.photos",
        ],
    ):
        try:
            _field_mask = ",".join(field_mask)
            print(_field_mask)
            headers = {
                "X-Goog-Api-Key": self.api_key,
                "Content-Type": "application/json",
                "X-Goog-FieldMask": _field_mask,
            }
            data = {"textQuery": text_query, "languageCode": "ja"}

            with httpx.Client() as client:
                response = client.post(
                    url="https://places.googleapis.com/v1/places:searchText",
                    headers=headers,
                    json=data,
                )
                print(f"status: {response.status_code}")
                print(f"data: {response.json()}")
        except Exception as e:
            print(e)

        def nearby_search():
            pass
