"""ConfidenceAgent — scores each field of the draft API for HITL highlighting."""

from agents.base import BaseAgent
from models.agent_session import AgentSession
from llm.client import chat_json
import json

SYSTEM = """You are an API quality reviewer. Given a draft API schema, score each
top-level field and each endpoint field for confidence.

Return a JSON object where each key is a dot-path field name and the value is:
{
  "score": 0-100,
  "status": "HIGH" | "MEDIUM" | "LOW" | "MISSING",
  "suggestion": "short fix suggestion or null"
}

Status rules:
  HIGH    = score >= 80  (field looks correct, no action needed)
  MEDIUM  = score 50-79  (field present but may need review)
  LOW     = score < 50   (field is uncertain or incomplete)
  MISSING = field is null or absent (user must fill in)

Evaluate: name, description, base_url, and for each endpoint:
  path, method, auth_type, input_schema, output_schema

Return a flat map with dot-notation keys, e.g.:
  "name", "base_url", "endpoints.0.path", "endpoints.0.auth_type", etc."""


class ConfidenceAgent(BaseAgent):
    name = "confidence_agent"

    async def run(self, session: AgentSession) -> AgentSession:
        user_msg = (
            "Draft API schema to score:\n"
            + json.dumps(session.draft_api, indent=2)
        )
        result = await chat_json(SYSTEM, user_msg, max_tokens=4096)
        session.confidence_map = result
        return session
