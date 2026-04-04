from pydantic import BaseModel, Field
from typing import List

import httpx


class RoutesClient(BaseModel):
    api_key: str = Field(...)

    def compute_routes(
        self,
        origin: dict,
        destination: dict,
        travel_mode: str = "DRIVE",
        language_code: str = "ja",
        field_mask: List[str] = [
            "routes.duration",
            "routes.distanceMeters",
            "routes.polyline.encodedPolyline",
        ],
    ):
        try:
            _field_mask = ",".join(field_mask)
            headers = {
                "X-Goog-Api-Key": self.api_key,
                "Content-Type": "application/json",
                "X-Goog-FieldMask": _field_mask,
            }
            data = {
                "origin": {
                    "location": {
                        "latLng": {
                            "latitude": origin["latitude"],
                            "longitude": origin["longitude"],
                        }
                    }
                },
                "destination": {
                    "location": {
                        "latLng": {
                            "latitude": destination["latitude"],
                            "longitude": destination["longitude"],
                        }
                    }
                },
                "travelMode": travel_mode,
                "languageCode": language_code,
            }

            with httpx.Client() as client:
                response = client.post(
                    url="https://routes.googleapis.com/directions/v2:computeRoutes",
                    headers=headers,
                    json=data,
                )
                print(f"status: {response.status_code}")
                print(f"data: {response.json()}")
                return response.json()
        except Exception as e:
            print(e)

    def compute_route_matrix(
        self,
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
    ):
        try:
            _field_mask = ",".join(field_mask)
            headers = {
                "X-Goog-Api-Key": self.api_key,
                "Content-Type": "application/json",
                "X-Goog-FieldMask": _field_mask,
            }
            data = {
                "origins": [
                    {
                        "waypoint": {
                            "location": {
                                "latLng": {
                                    "latitude": o["latitude"],
                                    "longitude": o["longitude"],
                                }
                            }
                        }
                    }
                    for o in origins
                ],
                "destinations": [
                    {
                        "waypoint": {
                            "location": {
                                "latLng": {
                                    "latitude": d["latitude"],
                                    "longitude": d["longitude"],
                                }
                            }
                        }
                    }
                    for d in destinations
                ],
                "travelMode": travel_mode,
            }

            with httpx.Client() as client:
                response = client.post(
                    url="https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
                    headers=headers,
                    json=data,
                )
                print(f"status: {response.status_code}")
                print(f"data: {response.json()}")
                return response.json()
        except Exception as e:
            print(e)
