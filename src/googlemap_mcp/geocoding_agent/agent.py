import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List

from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.tools.function_tool import FunctionTool

from googlemap_mcp.tools.geocoding import GeocodingClient

load_dotenv()

maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

geocoding_client = GeocodingClient(api_key=maps_api_key)


class GeocodingResult(BaseModel):
    address: str = Field(...)
    latitude: float = Field(...)
    longitude: float = Field(...)


class GeocodingResults(BaseModel):
    list: List[GeocodingResult]


geocoding_researcher = LlmAgent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful assistant for geocoding questions.",
    instruction="ユーザーの要望に応じて、GoogleMapを活用してジオコーディング（住所から座標への変換）やリバースジオコーディング（座標から住所への変換）を行ってください。",
    tools=[
        FunctionTool(geocoding_client.geocode),
        FunctionTool(geocoding_client.reverse_geocode),
    ],
    output_key="geocoding_result",
)

formater = LlmAgent(
    model="gemini-2.5-flash",
    name="formatter",
    description="",
    instruction="検索結果をJSON形式に整形して出力してください。{geocoding_result}",
    output_schema=GeocodingResults,
)

geocoding_search = SequentialAgent(
    name="geocoding_search", sub_agents=[geocoding_researcher, formater]
)

root_agent = geocoding_search
