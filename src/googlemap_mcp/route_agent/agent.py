import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List

from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.tools.function_tool import FunctionTool

from googlemap_mcp.tools.routes import RoutesClient

load_dotenv()

maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

routes_client = RoutesClient(api_key=maps_api_key)


class Route(BaseModel):
    duration: Optional[str] = Field(...)
    distanceMeters: Optional[int] = Field(...)
    polyline: Optional[str] = Field(...)


class Routes(BaseModel):
    list: List[Route]


route_researcher = LlmAgent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful assistant for route calculation.",
    instruction="ユーザーの要望に応じたルートを、GoogleMapを活用して計算してあげてください。",
    tools=[
        FunctionTool(routes_client.compute_routes),
        FunctionTool(routes_client.compute_route_matrix),
    ],
    output_key="route_search_result",
)

formater = LlmAgent(
    model="gemini-2.5-flash",
    name="formatter",
    description="",
    instruction="検索結果をJSON形式に整形して出力してください。{route_search_result}",
    output_schema=Routes,
)

route_search = SequentialAgent(
    name="route_search", sub_agents=[route_researcher, formater]
)

root_agent = route_search
