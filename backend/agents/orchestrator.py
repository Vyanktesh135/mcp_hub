"""
AgentOrchestrator — owns the full session lifecycle.

State machine:
  INIT → CLASSIFYING → PARSING → SCHEMA_GENERATING → CONFIDENCE_SCORING
       → HITL_PENDING   (pauses here, returns to caller)
       → VALIDATING     (resumes after human confirms)
       → SAVING → SAVED

On any agent error: state = FAILED, error logged, exception re-raised.
After a failed HITL validation: state = HITL_PENDING (loop back).
"""

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

from models.agent_session import AgentSession
from database import SessionLocal

from agents.input_classifier import InputClassifier
from agents.parsing_agent import ParsingAgent
from agents.schema_agent import SchemaAgent
from agents.confidence_agent import ConfidenceAgent
from agents.schema_validator import SchemaValidator
from agents.api_test_agent import ApiTestAgent
from agents.api_saver import ApiSaver


class AgentOrchestrator:

    def __init__(self, db: Session):
        self.db = db
        self._classifier  = InputClassifier()
        self._parser      = ParsingAgent()
        self._schema      = SchemaAgent()
        self._confidence  = ConfidenceAgent()
        self._validator   = SchemaValidator()
        self._api_tester  = ApiTestAgent()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start(
        self,
        *,
        raw_input: str | None = None,
        file_path: str | None = None,
    ) -> AgentSession:
        """
        Create a new session and run the pipeline up to HITL_PENDING.
        Returns the session in state HITL_PENDING (or FAILED on error).
        """
        session = AgentSession(
            id=str(uuid.uuid4()),
            raw_input=raw_input,
            file_path=file_path,
            state="INIT",
            error_log=[],
        )
        self.db.add(session)
        self.db.commit()

        await self._run_pre_hitl(session)
        return session

    async def confirm(
        self,
        session: AgentSession,
        human_edits: dict,
    ) -> AgentSession:
        """
        Resume a HITL_PENDING session with human edits.
        Runs validation → save. If validation fails, returns to HITL_PENDING.
        """
        if session.state != "HITL_PENDING":
            raise ValueError(
                f"Session {session.id} is in state '{session.state}', "
                "expected 'HITL_PENDING'."
            )

        session.human_edits = human_edits
        # merge edits into draft
        session.final_api = self._merge_edits(session.draft_api, human_edits)
        self._save(session)

        await self._run_post_hitl(session)
        return session

    def get(self, session_id: str) -> AgentSession | None:
        return self.db.get(AgentSession, session_id)

    # ------------------------------------------------------------------
    # Pre-HITL pipeline: CLASSIFY → PARSE → SCHEMA → CONFIDENCE
    # ------------------------------------------------------------------

    async def _run_pre_hitl(self, session: AgentSession) -> None:
        steps = [
            ("CLASSIFYING",        self._classifier),
            ("PARSING",            self._parser),
            ("SCHEMA_GENERATING",  self._schema),
            ("CONFIDENCE_SCORING", self._confidence),
        ]
        for state_name, agent in steps:
            await self._run_step(session, state_name, agent)
            if session.state == "FAILED":
                return

        session.state = "HITL_PENDING"
        self._save(session)

    # ------------------------------------------------------------------
    # Post-HITL pipeline: VALIDATE → API_TESTING → SAVE
    # ------------------------------------------------------------------

    async def _run_post_hitl(self, session: AgentSession) -> None:
        # 1. Rule-based schema validation
        await self._run_step(session, "VALIDATING", self._validator)
        if session.state == "FAILED":
            return

        if session.validation_errors:
            # Promote final_api → draft_api so the re-opened form shows the
            # user's last submission, not the original LLM/manual extraction.
            if session.final_api:
                session.draft_api = session.final_api
            session.state = "HITL_PENDING"
            self._save(session)
            return

        # 2. Live API test (informational — never blocks saving)
        await self._run_step(session, "API_TESTING", self._api_tester)
        if session.state == "FAILED":
            # API test agent errors are non-fatal; reset state and continue
            session.state = "VALIDATING"   # dummy state to satisfy _run_step pre-check
            session.api_test_results = []
            self._save(session)

        # 3. Save
        saver = ApiSaver(db=self.db)
        await self._run_step(session, "SAVING", saver)
        if session.state != "FAILED":
            session.state = "SAVED"
            self._save(session)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _run_step(
        self,
        session: AgentSession,
        state_name: str,
        agent,
    ) -> None:
        session.state = state_name
        session.updated_at = datetime.now(timezone.utc)
        self._save(session)
        try:
            await agent.run(session)
            self._save(session)
        except Exception as exc:
            friendly = _friendly_error(exc)
            session.log_error(state_name, friendly)
            session.state = "FAILED"
            self._save(session)
            # Do NOT re-raise — the session is persisted as FAILED.
            # Re-raising would propagate a 500 through the ASGI stack;
            # instead the route returns the FAILED session to the frontend.

    def _save(self, session: AgentSession) -> None:
        session.updated_at = datetime.now(timezone.utc)
        self.db.add(session)
        self.db.commit()

    # ------------------------------------------------------------------
    # Error helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _merge_edits(draft: dict | None, edits: dict) -> dict:
        """Shallow-merge human edits on top of the draft."""
        if not draft:
            return edits
        merged = dict(draft)
        for key, value in edits.items():
            if key == "endpoints" and isinstance(value, list):
                # Full replacement when the form sends the entire array (no _index keys).
                # Partial _index-based merge is kept for legacy callers.
                has_index = any(isinstance(ep, dict) and "_index" in ep for ep in value)
                if not has_index:
                    merged["endpoints"] = value
                else:
                    merged_endpoints = list(merged.get("endpoints", []))
                    for ep_edit in value:
                        idx = ep_edit.get("_index", 0)
                        if idx < len(merged_endpoints):
                            merged_endpoints[idx] = {**merged_endpoints[idx], **ep_edit}
                        else:
                            merged_endpoints.append(ep_edit)
                    merged["endpoints"] = merged_endpoints
            else:
                merged[key] = value
        return merged


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _friendly_error(exc: Exception) -> str:
    """Convert low-level exceptions to concise, user-readable messages."""
    msg = str(exc)

    # OpenAI rate limit / token limit
    if "rate_limit_exceeded" in msg or "RateLimitError" in type(exc).__name__:
        if "tokens" in msg:
            return (
                "File is too large for the LLM context window. "
                "Try a smaller file or remove unnecessary content."
            )
        return "LLM rate limit reached — please wait a moment and retry."

    # OpenAI API errors (bad key, quota, etc.)
    if "AuthenticationError" in type(exc).__name__:
        return "Invalid OpenAI API key. Check your OPENAI_API_KEY in backend/.env."

    if "APIStatusError" in type(exc).__name__ or "openai" in type(exc).__module__:
        return f"OpenAI API error: {msg[:200]}"

    # Generic fallback — keep it short
    return msg[:300]
