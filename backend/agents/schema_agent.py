"""
SchemaAgent — converts per-endpoint chunks into clean OpenAPI-compatible definitions.

Processes one endpoint per LLM call in parallel — never hits output token limits
regardless of how many endpoints the API has.
"""

import asyncio
import json
from agents.base import BaseAgent
from models.agent_session import AgentSession
from llm.client import chat_json

_META_SYSTEM = """You are an API schema designer.
Given API metadata, return a clean JSON object:
{
  "name": "Human-readable API name",
  "description": "What this API does in 1-2 sentences",
  "base_url": "https://api.example.com",
  "version": "1.0.0",
  "auth_type": "BEARER | API_KEY | BASIC | NONE"
}
Return ONLY the JSON object."""

_ENDPOINT_SYSTEM = """You are an API schema designer.
Convert the raw endpoint data into a clean OpenAPI-compatible definition.
Return a single JSON object:
{
  "name": "snake_case_function_name",
  "description": "what this endpoint does",
  "path": "/path/{id}",
  "method": "GET",
  "auth_type": "BEARER | API_KEY | BASIC | NONE",
  "input_schema": {
    "type": "object",
    "properties": {
      "param": {"type": "string", "description": "..."}
    },
    "required": ["param"]
  },
  "output_schema": {"type": "object", "properties": {}},
  "headers": []
}

CRITICAL RULES:
1. Include ALL parameters (path, query, body, header) in input_schema.properties.
2. required[] must list every truly required parameter — never empty for POST/PUT/PATCH.
3. Path params like {id} must be in properties AND in required[].
4. Use types: string | integer | number | boolean | array | object.
5. Never return empty properties if the source shows parameters exist.
Return ONLY the JSON object."""


_MAX_CONCURRENT = 8  # cap parallel LLM calls to avoid rate limits


class SchemaAgent(BaseAgent):
    name = "schema_agent"

    async def run(self, session: AgentSession) -> AgentSession:
        extracted = session.extracted_schema or {}
        chunks = extracted.get("_chunks", [])

        if not chunks:
            raise ValueError("No endpoint chunks found — ParsingAgent may have failed.")

        sem = asyncio.Semaphore(_MAX_CONCURRENT)

        async def _throttled(c):
            async with sem:
                return await self._build_endpoint(c)

        meta_task = self._build_meta(extracted)
        endpoint_tasks = [_throttled(c) for c in chunks]

        meta, *endpoints = await asyncio.gather(meta_task, *endpoint_tasks)

        # Filter out any failed individual endpoint schemas
        valid_endpoints = [ep for ep in endpoints if ep and ep.get("path")]

        session.draft_api = {
            "name":        meta.get("name") or extracted.get("name", ""),
            "description": meta.get("description", ""),
            "base_url":    meta.get("base_url") or extracted.get("base_url", ""),
            "version":     meta.get("version", "1.0.0"),
            "auth_type":   meta.get("auth_type") or extracted.get("auth_type", "NONE"),
            "endpoints":   valid_endpoints,
        }
        return session

    async def _build_meta(self, extracted: dict) -> dict:
        prompt = json.dumps({
            "name":     extracted.get("name", ""),
            "base_url": extracted.get("base_url", ""),
            "auth_type": extracted.get("auth_type", ""),
        })
        try:
            return await chat_json(_META_SYSTEM, prompt, max_tokens=512)
        except Exception:
            return {}

    async def _build_endpoint(self, chunk: dict) -> dict | None:
        try:
            result = await chat_json(
                _ENDPOINT_SYSTEM,
                f"Endpoint: {chunk['hint']}\n\nRaw data:\n{chunk['content']}",
                max_tokens=2048,
            )
            # Ensure method and path are always set from chunk (source of truth)
            result.setdefault("method", chunk["method"])
            result.setdefault("path",   chunk["path"])
            return result
        except Exception:
            return None
