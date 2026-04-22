"""SchemaAgent — converts extracted schema into a clean OpenAPI-compatible draft."""

from agents.base import BaseAgent
from models.agent_session import AgentSession
from llm.client import chat_json
import json

SYSTEM = """You are an API schema designer. Given a raw extracted API structure,
produce a clean, well-named OpenAPI-compatible API definition.

Return a JSON object with this exact shape:
{
  "name": "Human-readable API name",
  "description": "What this API does in 1-2 sentences",
  "base_url": "https://api.example.com",
  "version": "1.0.0",
  "auth_type": "BEARER | API_KEY | BASIC | NONE",
  "endpoints": [
    {
      "name": "snake_case_function_name",
      "description": "what this endpoint does",
      "path": "/path/{id}",
      "method": "GET",
      "auth_type": "BEARER | API_KEY | BASIC | NONE",
      "input_schema": {
        "type": "object",
        "properties": {
          "param": { "type": "string", "description": "..." }
        },
        "required": ["param"]
      },
      "output_schema": {
        "type": "object",
        "properties": {}
      },
      "headers": []
    }
  ]
}

CRITICAL RULES for input_schema — this is what an LLM uses to know what arguments to pass:

1. INCLUDE ALL PARAMETERS regardless of location (query, path, body, header).
   - Path params like {id}: include in properties, mark required=true.
   - Body params for POST/PUT/PATCH: MUST be included in properties — this is the most
     commonly missed case. If the raw input has body params, every one must appear here.
   - Query params: include all, with correct required flags.

2. REQUIRED ARRAY must list every parameter that is truly required.
   - An empty "required": [] on a POST endpoint is almost always wrong.
   - If a body field is marked required in the source, it must be in "required".

3. TYPES: use "string", "integer", "number", "boolean", "array", "object".
   - For arrays, add "items": {"type": "string"} (or appropriate item type).

4. NEVER return an endpoint with "properties": {} if the raw input shows parameters exist.
   Go back and check the raw extracted parameters for that endpoint.

Use descriptive names. Keep descriptions concise but accurate."""


class SchemaAgent(BaseAgent):
    name = "schema_agent"

    async def run(self, session: AgentSession) -> AgentSession:
        user_msg = (
            "Extracted API structure:\n"
            + json.dumps(session.extracted_schema, indent=2)
        )
        result = await chat_json(SYSTEM, user_msg, max_tokens=4096)
        session.draft_api = result
        return session
