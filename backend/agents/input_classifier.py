"""InputClassifier — determines DOC vs CHAT mode and normalises raw_input."""

import os
from agents.base import BaseAgent
from models.agent_session import AgentSession

# ~60 k chars ≈ 15 k tokens — keeps total request well under 30 k TPM.
# A note is appended so the LLM knows the content was cut.
MAX_INPUT_CHARS = 60_000


class InputClassifier(BaseAgent):
    name = "input_classifier"

    async def run(self, session: AgentSession) -> AgentSession:
        if session.file_path and os.path.exists(session.file_path):
            session.mode = "DOC"
            session.raw_input = self._read_file(session.file_path)
        else:
            session.mode = "CHAT"
            # raw_input already set by caller (chat messages joined as text)

        return session

    def _read_file(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()

        if ext in (".txt", ".md", ".yaml", ".yml", ".json"):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        elif ext == ".pdf":
            content = self._read_pdf(path)
        else:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

        return self._truncate(content)

    def _read_pdf(self, path: str) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            return f"[PDF file at {path} — install pypdf to extract text]"

    @staticmethod
    def _truncate(text: str) -> str:
        if len(text) <= MAX_INPUT_CHARS:
            return text
        note = (
            f"\n\n[NOTE: Content truncated from {len(text):,} to {MAX_INPUT_CHARS:,} "
            "characters to fit model context. Extract endpoints from the visible portion.]"
        )
        return text[:MAX_INPUT_CHARS] + note
