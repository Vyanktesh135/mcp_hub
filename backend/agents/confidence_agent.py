"""ConfidenceAgent — scores each field of the draft API for HITL highlighting."""

from agents.base import BaseAgent
from models.agent_session import AgentSession
from llm.client import chat_json
import json

_META_SYSTEM = """You are an API quality reviewer. Score the top-level fields of this API schema.

Return a JSON object where each key is a field name and the value is:
{"score": 0-100, "status": "HIGH"|"MEDIUM"|"LOW"|"MISSING", "suggestion": "short fix or null"}

Status rules: HIGH>=80, MEDIUM 50-79, LOW<50, MISSING=null/absent.
Evaluate only: name, description, base_url, auth_type.
Return ONLY the JSON object."""


def _score_endpoints(endpoints: list) -> dict:
    """Rule-based endpoint scoring — works for any number of endpoints without LLM."""
    result = {}
    for i, ep in enumerate(endpoints):
        prefix = f"endpoints.{i}"
        for field in ("name", "path", "method", "auth_type"):
            val = ep.get(field)
            if not val:
                result[f"{prefix}.{field}"] = {
                    "score": 0, "status": "MISSING",
                    "suggestion": f"Add {field}",
                }
            else:
                result[f"{prefix}.{field}"] = {
                    "score": 90, "status": "HIGH", "suggestion": None,
                }
        props = (ep.get("input_schema") or {}).get("properties") or {}
        if not props:
            result[f"{prefix}.input_schema"] = {
                "score": 30, "status": "LOW",
                "suggestion": "Add input parameters",
            }
        else:
            result[f"{prefix}.input_schema"] = {
                "score": 80, "status": "HIGH", "suggestion": None,
            }
        out_props = (ep.get("output_schema") or {}).get("properties") or {}
        if not out_props:
            result[f"{prefix}.output_schema"] = {
                "score": 40, "status": "MEDIUM",
                "suggestion": "Add output schema",
            }
        else:
            result[f"{prefix}.output_schema"] = {
                "score": 80, "status": "HIGH", "suggestion": None,
            }
    return result


class ConfidenceAgent(BaseAgent):
    name = "confidence_agent"

    async def run(self, session: AgentSession) -> AgentSession:
        draft = session.draft_api or {}
        endpoints = draft.get("endpoints", [])

        # LLM scores only the 4 top-level metadata fields — bounded, never truncates
        meta_prompt = json.dumps({
            k: draft.get(k) for k in ("name", "description", "base_url", "auth_type")
        }, indent=2)
        try:
            meta_scores = await chat_json(_META_SYSTEM, meta_prompt, max_tokens=512)
        except Exception:
            meta_scores = {}

        session.confidence_map = {**meta_scores, **_score_endpoints(endpoints)}
        return session
