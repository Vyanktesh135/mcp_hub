"""ParsingAgent — extracts API structure from raw text using LLM."""

from agents.base import BaseAgent
from models.agent_session import AgentSession
from llm.client import chat_json

SYSTEM = """You are an expert API analyst. Given API documentation, a Swagger/OpenAPI file,
or a natural-language description, extract ALL API information precisely.

Return a JSON object with this exact shape:
{
  "base_url": "string or null",
  "auth_type": "BEARER | API_KEY | BASIC | NONE | UNKNOWN",
  "endpoints": [
    {
      "path": "/resource/{id}",
      "method": "GET | POST | PUT | DELETE | PATCH",
      "name": "snake_case_name",
      "description": "what this endpoint does",
      "parameters": [
        {
          "name": "param_name",
          "type": "string | integer | boolean | array | object",
          "required": true,
          "location": "query | body | path | header",
          "description": "what this param does"
        }
      ],
      "response_example": {}
    }
  ]
}

CRITICAL RULES — follow these exactly:

1. REQUEST BODY PARAMETERS (most commonly missed):
   - For POST, PUT, PATCH endpoints, ALWAYS extract every field from the request body.
   - Mark them with "location": "body".
   - These are just as required as query/path params — do NOT skip them.
   - If a body field is listed as required in the docs, set "required": true.
   - Example: POST /annotation-queues expects body fields "name" (string, required)
     and "scoreConfigIds" (array, required) — both must appear in parameters.

2. PATH PARAMETERS:
   - Any {param} token in the path must appear in parameters with "location": "path", "required": true.

3. QUERY PARAMETERS:
   - Extract all documented query params with correct types and required flags.

4. REQUIRED vs OPTIONAL:
   - Only mark "required": true if the docs explicitly say the field is required or mandatory.
   - Optional fields should be "required": false.

5. TYPES:
   - Use "array" for lists/arrays. If the array items have a known type, note it in description.
   - Use "object" for nested objects.

If any field is genuinely unknown, use null. Do not invent information not present in the source."""


class ParsingAgent(BaseAgent):
    name = "parsing_agent"

    async def run(self, session: AgentSession) -> AgentSession:
        user_msg = (
            f"Mode: {session.mode}\n\n"
            f"Input text:\n{session.raw_input or ''}"
        )
        result = await chat_json(SYSTEM, user_msg, max_tokens=4096)
        session.extracted_schema = result
        return session
