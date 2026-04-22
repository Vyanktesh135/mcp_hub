import json
import re
import httpx
from typing import Any
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from openai import AsyncOpenAI

from config import settings
from database import get_db
from utils.encryption import decrypt_creds
from models.api_definition import ApiDefinition, ApiEndpoint
from models.chatgpt_connection import ChatGPTConnection, ToolCallLog
from translators.openai_translator import api_to_tools, resolve_tool_call
from schemas.chatgpt import (
    ConnectResponse, ChatRequest, ChatResponse,
    StatsResponse, ToolCallRecord,
)
from utils.auth import get_current_user
from models.user import User
from context.context_layer import context_layer

router = APIRouter(prefix="/api/chatgpt", tags=["chatgpt"])


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_api_ids = [
        a.id for a in db.query(ApiDefinition.id).filter(ApiDefinition.user_id == current_user.id).all()
    ]
    total_apis = len(user_api_ids)
    connected = db.query(ChatGPTConnection).filter(
        ChatGPTConnection.user_id == current_user.id,
        ChatGPTConnection.is_active == True,
    ).count()
    calls = db.query(ToolCallLog).filter(ToolCallLog.api_definition_id.in_(user_api_ids)).count()
    return StatsResponse(total_apis=total_apis, connected_apis=connected, total_tool_calls=calls)


# ── Registry with connection status ───────────────────────────────────────────

@router.get("/registry")
def list_all_with_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    apis = (
        db.query(ApiDefinition)
        .filter(ApiDefinition.user_id == current_user.id)
        .order_by(ApiDefinition.created_at.desc())
        .all()
    )
    connected_ids = {
        c.api_definition_id
        for c in db.query(ChatGPTConnection).filter(
            ChatGPTConnection.user_id == current_user.id,
            ChatGPTConnection.is_active == True,
        ).all()
    }
    return [
        {
            "id": api.id,
            "name": api.name,
            "description": api.description,
            "base_url": api.base_url,
            "visibility": api.visibility,
            "endpoint_count": len(api.endpoints),
            "is_connected": api.id in connected_ids,
            "tools": api_to_tools(api),
        }
        for api in apis
    ]


# ── Connect / Disconnect ───────────────────────────────────────────────────────

@router.post("/connect/{api_id}", response_model=ConnectResponse)
def connect_api(
    api_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api = db.query(ApiDefinition).filter(
        ApiDefinition.id == api_id, ApiDefinition.user_id == current_user.id
    ).first()
    if not api:
        raise HTTPException(404, "API not found")

    existing = db.query(ChatGPTConnection).filter(
        ChatGPTConnection.api_definition_id == api_id,
        ChatGPTConnection.user_id == current_user.id,
        ChatGPTConnection.is_active == True,
    ).first()
    if existing:
        return ConnectResponse(api_definition_id=api_id, connected=True, message="Already connected")

    db.add(ChatGPTConnection(id=str(uuid4()), api_definition_id=api_id, user_id=current_user.id))
    db.commit()
    return ConnectResponse(
        api_definition_id=api_id,
        connected=True,
        message=f"Connected — {len(api.endpoints)} tool(s) available",
    )


@router.delete("/disconnect/{api_id}", response_model=ConnectResponse)
def disconnect_api(
    api_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conn = db.query(ChatGPTConnection).filter(
        ChatGPTConnection.api_definition_id == api_id,
        ChatGPTConnection.user_id == current_user.id,
        ChatGPTConnection.is_active == True,
    ).first()
    if not conn:
        raise HTTPException(404, "Connection not found")
    conn.is_active = False
    db.commit()
    return ConnectResponse(api_definition_id=api_id, connected=False, message="Disconnected")


# ── Session management ────────────────────────────────────────────────────────

@router.get("/session/{session_id}")
def get_session_info(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    info = context_layer.session_info(session_id)
    if not info:
        raise HTTPException(404, "Session not found or expired")
    return info


@router.delete("/session/{session_id}")
def clear_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    context_layer.clear_session(session_id)
    return {"cleared": True, "session_id": session_id}


# ── Tool schema export ─────────────────────────────────────────────────────────

@router.get("/tools/{api_id}")
def get_tools_schema(
    api_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api = db.query(ApiDefinition).filter(
        ApiDefinition.id == api_id, ApiDefinition.user_id == current_user.id
    ).first()
    if not api:
        raise HTTPException(404, "API not found")
    return {"api_id": api_id, "api_name": api.name, "tools": api_to_tools(api)}


# ── Parameter validation ───────────────────────────────────────────────────────

def _missing_required_params(ep: ApiEndpoint, arguments: dict) -> list[str]:
    schema = ep.input_schema or {}
    required = schema.get("required") or []
    return [p for p in required if p not in arguments or arguments[p] is None]


def _missing_params_message(ep: ApiEndpoint, missing: list[str]) -> str:
    schema   = ep.input_schema or {}
    props    = schema.get("properties") or {}
    details  = []
    for name in missing:
        prop  = props.get(name, {})
        ptype = prop.get("type", "string")
        desc  = prop.get("description", "")
        entry = f'"{name}" ({ptype})'
        if desc:
            entry += f" — {desc}"
        details.append(entry)

    return json.dumps({
        "status":  "MISSING_REQUIRED_PARAMETERS",
        "tool":    ep.name,
        "missing": missing,
        "details": details,
        "message": (
            f"Cannot call '{ep.name}' — the following required parameters are missing: "
            + ", ".join(missing)
            + ". Please ask the user to provide them before retrying."
        ),
    })


# ── Execution helper ───────────────────────────────────────────────────────────

async def _execute_tool(api: ApiDefinition, ep: ApiEndpoint, arguments: dict) -> tuple[str, bool]:
    if not api.base_url:
        return "Error: API has no base_url configured", False

    url = f"{api.base_url.rstrip('/')}{ep.path}"
    args = dict(arguments)

    for param in re.findall(r"\{(\w+)\}", ep.path):
        if param in args:
            url = url.replace(f"{{{param}}}", str(args.pop(param)))

    req_auth, extra_headers, extra_params = _build_auth(decrypt_creds(ep.auth_credentials))
    if extra_params:
        args.update(extra_params)

    try:
        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            method = ep.method.upper()
            if method == "GET":
                resp = await client.get(url, params=args, auth=req_auth, headers=extra_headers)
            elif method == "DELETE":
                resp = await client.delete(url, params=args, auth=req_auth, headers=extra_headers)
            else:
                resp = await client.request(method, url, json=args, auth=req_auth, headers=extra_headers)

        return resp.text[:2000], resp.status_code < 400
    except Exception as exc:
        return f"Request failed: {exc}", False


def _is_query_relevant(message: str, tools: list) -> bool:
    msg_words = set(
        w for w in re.sub(r"[^\w\s]", " ", message.lower()).split()
        if len(w) > 3
    )
    if not msg_words:
        return False

    for tool in tools:
        fn = tool.get("function", {})
        name  = fn.get("name", "").lower().replace("_", " ")
        desc  = fn.get("description", "").lower()
        param_text = " ".join(
            f"{k} {v.get('description', '')}"
            for k, v in (fn.get("parameters", {}).get("properties") or {}).items()
        ).lower()
        combined = f"{name} {desc} {param_text}"
        tool_words = set(
            w for w in re.sub(r"[^\w\s]", " ", combined).split()
            if len(w) > 3
        )
        if msg_words & tool_words:
            return True

    return False


def _build_auth(creds: dict | None) -> tuple:
    if not creds:
        return None, {}, {}
    ctype = (creds.get("type") or "none").lower()
    if ctype == "basic":
        return httpx.BasicAuth(creds.get("username", ""), creds.get("password", "")), {}, {}
    if ctype == "bearer":
        return None, {"Authorization": f"Bearer {creds.get('token', '')}"}, {}
    if ctype == "api_key":
        header = creds.get("header_name", "X-API-Key")
        return None, {header: creds.get("value", "")}, {}
    if ctype == "api_key_query":
        return None, {}, {creds.get("param_name", "api_key"): creds.get("value", "")}
    return None, {}, {}


# ── Chat with tools (agentic loop) ────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat_with_tools(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if req.api_ids:
        apis = db.query(ApiDefinition).filter(
            ApiDefinition.id.in_(req.api_ids), ApiDefinition.user_id == current_user.id
        ).all()
    else:
        cids = [
            c.api_definition_id
            for c in db.query(ChatGPTConnection).filter(
                ChatGPTConnection.user_id == current_user.id,
                ChatGPTConnection.is_active == True,
            ).all()
        ]
        apis = db.query(ApiDefinition).filter(ApiDefinition.id.in_(cids)).all()

    all_tools = []
    for api in apis:
        all_tools.extend(api_to_tools(api))

    if not all_tools:
        return ChatResponse(response="", tool_calls=[], model="none", status="NO_TOOLS_CONNECTED")

    if not _is_query_relevant(req.message, all_tools):
        return ChatResponse(
            response="",
            tool_calls=[],
            model="none",
            status="NO_RELEVANT_TOOL",
            available_tools=[t["function"]["name"] for t in all_tools],
        )

    if settings.mock_llm or not settings.openai_api_key or settings.openai_api_key == "mock":
        return ChatResponse(
            response=(
                f"[Mock mode] I have {len(all_tools)} tool(s) available to answer: '{req.message}'. "
                "Set MOCK_LLM=false and OPENAI_API_KEY in backend/.env to use real GPT-4o."
            ),
            tool_calls=[],
            model="mock",
            session_id=req.session_id or "",
        )

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # ── Context Layer: inject history + system prompt ─────────────────────────
    session_id, messages = context_layer.build_messages(
        session_id=req.session_id,
        user_message=req.message,
        apis=apis,
        user_email=current_user.email,
    )

    records: list[ToolCallRecord] = []
    tool_messages_this_turn: list[dict] = []
    final_assistant_msg: dict = {}

    for _ in range(5):
        kwargs: dict = {"model": "gpt-4o", "messages": messages}
        if all_tools:
            kwargs["tools"] = all_tools
            kwargs["tool_choice"] = "auto"

        resp = await client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message

        if not msg.tool_calls:
            final_assistant_msg = {"role": "assistant", "content": msg.content or ""}
            context_layer.save_turn(
                session_id, req.message, final_assistant_msg, tool_messages_this_turn
            )
            return ChatResponse(
                response=msg.content or "",
                tool_calls=records,
                model="gpt-4o",
                session_id=session_id,
            )

        assistant_dict = msg.model_dump(exclude_unset=True)
        messages.append(assistant_dict)

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            api_obj, ep_obj = resolve_tool_call(tc.function.name, db)

            if api_obj and ep_obj:
                missing = _missing_required_params(ep_obj, args)
                if missing:
                    result_text = _missing_params_message(ep_obj, missing)
                    success = False
                else:
                    result_text, success = await _execute_tool(api_obj, ep_obj, args)
                db.add(ToolCallLog(
                    id=str(uuid4()),
                    api_definition_id=api_obj.id,
                    endpoint_name=ep_obj.name or ep_obj.path,
                    arguments=json.dumps(args),
                    result=result_text[:1000],
                    success=success,
                ))
                db.commit()
            else:
                result_text, success = "Tool not found", False

            records.append(ToolCallRecord(
                tool_name=tc.function.name,
                api_name=api_obj.name if api_obj else "unknown",
                endpoint=ep_obj.name or ep_obj.path if ep_obj else tc.function.name,
                arguments=args,
                result=result_text,
                success=success,
            ))
            tool_msg = {"role": "tool", "tool_call_id": tc.id, "content": result_text}
            messages.append(tool_msg)
            tool_messages_this_turn.append(tool_msg)

    final = await client.chat.completions.create(model="gpt-4o", messages=messages)
    final_assistant_msg = {"role": "assistant", "content": final.choices[0].message.content or ""}
    context_layer.save_turn(
        session_id, req.message, final_assistant_msg, tool_messages_this_turn
    )
    return ChatResponse(
        response=final.choices[0].message.content or "",
        tool_calls=records,
        model="gpt-4o",
        session_id=session_id,
    )
