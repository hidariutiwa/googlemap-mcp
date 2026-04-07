import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List

from google.adk.agents import SequentialAgent, LoopAgent, LlmAgent
from google.adk.tools.function_tool import FunctionTool

from googlemap_mcp.tools.places import PlacesClient
from googlemap_mcp.tools.routes import RoutesClient
from googlemap_mcp.tools.geocoding import GeocodingClient

load_dotenv()

maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

places_client = PlacesClient(api_key=maps_api_key)
routes_client = RoutesClient(api_key=maps_api_key)
geocoding_client = GeocodingClient(api_key=maps_api_key)


class Place(BaseModel):
    name: str = Field(...)
    address: str = Field(...)
    bussiness_hour: Optional[str] = Field(...)
    budget: Optional[float] = Field(...)


class Places(BaseModel):
    list: List[Place]


place_researcher = LlmAgent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful assistant for user questions.",
    instruction="ユーザーの要望に応じた場所を、GoogleMapを活用して探してあげてください。",
    tools=[FunctionTool(places_client.text_search)],
    output_key="place_search_result",
)

formater = LlmAgent(
    model="gemini-2.5-flash",
    name="formatter",
    description="",
    instruction="検索結果をJSON形式に整形して出力してください。{place_search_result}",
    output_schema=Places,
)

place_search = SequentialAgent(
    name="place_search", sub_agents=[place_researcher, formater]
)

root_agent = place_search
