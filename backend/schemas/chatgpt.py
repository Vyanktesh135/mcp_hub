from pydantic import BaseModel
from typing import Any


class ConnectResponse(BaseModel):
    api_definition_id: str
    connected: bool
    message: str


class ToolCallRecord(BaseModel):
    tool_name: str
    api_name: str
    endpoint: str
    arguments: dict[str, Any]
    result: str
    success: bool


class ChatRequest(BaseModel):
    message: str
    api_ids: list[str] = []  # empty = use all connected APIs


class ChatResponse(BaseModel):
    response: str
    tool_calls: list[ToolCallRecord]
    model: str
    status: str = "ok"               # "ok" | "NO_TOOLS_CONNECTED" | "NO_RELEVANT_TOOL"
    available_tools: list[str] = []  # tool names when status == NO_RELEVANT_TOOL


class StatsResponse(BaseModel):
    total_apis: int
    connected_apis: int
    total_tool_calls: int
