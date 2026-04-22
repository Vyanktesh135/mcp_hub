"""
MCP Hub — Use Case 2: Tool Creation via Doc Upload
Renders to: Docs/images/usecase2_doc_upload.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

W, H = 22, 17
BG = "#f6f8fa"

C = {
    "user":     {"bg": "#ffffff", "bd": "#94a3b8", "hi": "#1e293b", "lo": "#64748b"},
    "frontend": {"bg": "#eff6ff", "bd": "#3b82f6", "hi": "#1d4ed8", "lo": "#2563eb"},
    "backend":  {"bg": "#f0fdf4", "bd": "#16a34a", "hi": "#14532d", "lo": "#166534"},
    "agent":    {"bg": "#f5f3ff", "bd": "#7c3aed", "hi": "#4c1d95", "lo": "#6d28d9"},
    "external": {"bg": "#fffbeb", "bd": "#d97706", "hi": "#78350f", "lo": "#92400e"},
    "db":       {"bg": "#f0f9ff", "bd": "#0284c7", "hi": "#0c4a6e", "lo": "#0369a1"},
    "comp_fe":  {"bg": "#dbeafe", "bd": "#93c5fd", "hi": "#1e40af", "lo": "#2563eb"},
    "comp_be":  {"bg": "#dcfce7", "bd": "#86efac", "hi": "#14532d", "lo": "#15803d"},
    "comp_ag":  {"bg": "#ede9fe", "bd": "#c4b5fd", "hi": "#3b0764", "lo": "#6d28d9"},
    "comp_ext": {"bg": "#fef3c7", "bd": "#fcd34d", "hi": "#451a03", "lo": "#92400e"},
    "comp_db":  {"bg": "#e0f2fe", "bd": "#7dd3fc", "hi": "#0c4a6e", "lo": "#0369a1"},
    "comp":     {"bg": "#f8fafc", "bd": "#cbd5e1", "hi": "#1e293b", "lo": "#64748b"},
    "llm":      {"bg": "#fef3c7", "bd": "#f59e0b", "hi": "#78350f", "lo": "#92400e"},
}
TEXT  = "#0f172a"
MUTED = "#475569"
DIM   = "#94a3b8"

fig = plt.figure(figsize=(W, H), facecolor=BG, dpi=200)
ax  = fig.add_subplot(111, facecolor=BG)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1)

def box(x, y, w, h, key="comp", lw=1.3, z=3, r=0.15):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        fc=C[key]["bg"], ec=C[key]["bd"], lw=lw,
        zorder=z, clip_on=False,
    ))

def txt(x, y, s, color=TEXT, sz=7, w="normal", ha="center", va="center", z=10, mono=False):
    ax.text(x, y, s, color=color, fontsize=sz, fontweight=w,
            ha=ha, va=va, zorder=z, clip_on=False,
            fontfamily="monospace" if mono else "sans-serif")

def arrow(x1, y1, x2, y2, color=DIM, lw=1.3, dash=False):
    props = dict(arrowstyle="->", color=color, lw=lw, mutation_scale=10)
    if dash:
        props["linestyle"] = "dashed"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=props, zorder=6, annotation_clip=False)

def hline(y, color="#cbd5e1", lw=0.8):
    ax.plot([0.4, W - 0.4], [y, y], color=color, lw=lw, zorder=1)

def step_badge(x, y, num, color):
    ax.add_patch(FancyBboxPatch((x - 0.22, y - 0.22), 0.44, 0.44,
        boxstyle="round,pad=0,rounding_size=0.1",
        fc=color, ec="none", zorder=12, clip_on=False))
    ax.text(x, y, str(num), color="white", fontsize=7, fontweight="bold",
            ha="center", va="center", zorder=13, clip_on=False)

def llm_tag(x, y):
    box(x, y, 1.3, 0.34, "llm", lw=0.5, z=8, r=0.06)
    txt(x + 0.65, y + 0.17, "GPT-4o", C["external"]["hi"], sz=6, w="bold")

# ── Title ──────────────────────────────────────────────────────────────────────
txt(W / 2, 16.55, "MCP HUB  —  Use Case 2", TEXT, sz=18, w="bold", mono=True)
txt(W / 2, 16.05, "Tool Creation via Doc Upload  ·  Full AI pipeline  ·  3× GPT-4o calls", MUTED, sz=9.5)
hline(15.78)

step_x = 0.55
ROW = [14.6, 12.8, 11.0, 9.2, 7.4, 5.6, 3.8, 1.9]
RH  = 1.2

# ── Step 1 — Doc Upload frontend ──────────────────────────────────────────────
r = 0
box(1.0, ROW[r], 20.0, RH, "frontend", lw=1.6, z=2, r=0.18)
txt(11.0, ROW[r] + RH - 0.22, "FRONTEND  ·  Doc Upload  (/create/upload)", C["frontend"]["hi"], sz=8, w="bold", ha="center")
step_badge(step_x, ROW[r] + RH / 2, 1, C["frontend"]["bd"])

items = [
    ("Drag & Drop", "PDF / YAML / JSON\nTXT / Markdown"),
    ("File preview", "filename · size\ntype indicator"),
    ("POST multipart", "POST /api/agent/upload\nJWT Bearer"),
    ("Poll status", "GET /api/agent/:id\nevery 2s while processing"),
]
iw = 4.6
for i, (label, detail) in enumerate(items):
    ix = 1.2 + i * (iw + 0.1)
    box(ix, ROW[r] + 0.1, iw, 0.72, "comp_fe", lw=0.7, z=4, r=0.09)
    txt(ix + iw / 2, ROW[r] + 0.58, label,  C["frontend"]["hi"], sz=7, w="bold")
    txt(ix + iw / 2, ROW[r] + 0.26, detail, DIM,                sz=6.2, mono=True)
arrow(11.0, ROW[r], 11.0, ROW[r] - 0.28, C["frontend"]["bd"])

# ── Step 2 — Backend receives file ────────────────────────────────────────────
r = 1
box(1.0, ROW[r], 20.0, RH, "backend", lw=1.6, z=2, r=0.18)
txt(11.0, ROW[r] + RH - 0.22, "BACKEND  ·  POST /api/agent/upload  →  start_upload()", C["backend"]["hi"], sz=8, w="bold", ha="center")
step_badge(step_x, ROW[r] + RH / 2, 2, C["backend"]["bd"])

items2 = [
    ("File saved", "tmp disk path\n/tmp/upload_xxx"),
    ("AgentSession", "state=INIT\ncreated in DB"),
    ("Background task", "FastAPI BackgroundTasks\norch.start(file_path)"),
    ("Response 202", "session_id returned\nfrontend polls /status"),
]
for i, (label, detail) in enumerate(items2):
    ix = 1.2 + i * (iw + 0.1)
    box(ix, ROW[r] + 0.1, iw, 0.72, "comp_be", lw=0.7, z=4, r=0.09)
    txt(ix + iw / 2, ROW[r] + 0.58, label,  C["backend"]["hi"], sz=7, w="bold")
    txt(ix + iw / 2, ROW[r] + 0.26, detail, MUTED,              sz=6.2)
arrow(11.0, ROW[r], 11.0, ROW[r] - 0.28, C["agent"]["bd"])

# ── Step 3 — InputClassifier ──────────────────────────────────────────────────
r = 2
box(1.0, ROW[r], 20.0, RH, "agent", lw=1.6, z=2, r=0.18)
txt(11.0, ROW[r] + RH - 0.22, "STAGE 1  ·  CLASSIFYING  →  InputClassifier  (no LLM)", C["agent"]["hi"], sz=8, w="bold", ha="center")
step_badge(step_x, ROW[r] + RH / 2, 3, C["agent"]["bd"])

items3 = [
    ("PDF", "pypdf.PdfReader\nextract all pages"),
    ("YAML / JSON", "yaml.safe_load\nor json.loads"),
    ("TXT / MD", "open().read()\nraw text"),
    ("Truncate", "max 60,000 chars\nprevents token overflow"),
    ("extracted_schema", "saved to\nAgentSession"),
]
iw3 = 3.7
for i, (label, detail) in enumerate(items3):
    ix = 1.2 + i * (iw3 + 0.08)
    box(ix, ROW[r] + 0.1, iw3, 0.72, "comp_ag", lw=0.7, z=4, r=0.09)
    txt(ix + iw3 / 2, ROW[r] + 0.58, label,  C["agent"]["hi"], sz=7, w="bold")
    txt(ix + iw3 / 2, ROW[r] + 0.26, detail, MUTED,            sz=6)
arrow(11.0, ROW[r], 11.0, ROW[r] - 0.28, C["agent"]["bd"])

# ── Step 4 — ParsingAgent + SchemaAgent (LLM 1+2) ────────────────────────────
r = 3
box(1.0, ROW[r], 20.0, RH, "agent", lw=1.6, z=2, r=0.18)
txt(11.0, ROW[r] + RH - 0.22, "STAGE 2 + 3  ·  PARSING → SCHEMA_GENERATING  (2× GPT-4o)", C["agent"]["hi"], sz=8, w="bold", ha="center")
step_badge(step_x, ROW[r] + RH / 2, 4, C["agent"]["bd"])

# Left: ParsingAgent
box(1.2, ROW[r] + 0.1, 8.8, 0.72, "llm", lw=1.0, z=4, r=0.09)
txt(5.6, ROW[r] + 0.62, "ParsingAgent  ·  GPT-4o call #1", C["external"]["hi"], sz=7.5, w="bold")
txt(5.6, ROW[r] + 0.36, "Extract endpoints · paths · methods · params from raw text", MUTED, sz=6.3)
txt(5.6, ROW[r] + 0.18, "Output: raw structure saved as extracted_schema", DIM, sz=6, mono=True)
llm_tag(8.4, ROW[r] + 0.62)

# Right: SchemaAgent
box(10.3, ROW[r] + 0.1, 10.5, 0.72, "llm", lw=1.0, z=4, r=0.09)
txt(15.55, ROW[r] + 0.62, "SchemaAgent  ·  GPT-4o call #2", C["external"]["hi"], sz=7.5, w="bold")
txt(15.55, ROW[r] + 0.36, "Convert to OpenAPI-compatible JSON  ·  input_schema with type/properties/required", MUTED, sz=6.3)
txt(15.55, ROW[r] + 0.18, "Output: draft_api saved to AgentSession", DIM, sz=6, mono=True)
llm_tag(19.2, ROW[r] + 0.62)

arrow(10.0, ROW[r] + 0.46, 10.3, ROW[r] + 0.46, C["external"]["lo"])
arrow(11.0, ROW[r], 11.0, ROW[r] - 0.28, C["agent"]["bd"])

# ── Step 5 — ConfidenceAgent ──────────────────────────────────────────────────
r = 4
box(1.0, ROW[r], 20.0, RH, "agent", lw=1.6, z=2, r=0.18)
txt(11.0, ROW[r] + RH - 0.22, "STAGE 4  ·  CONFIDENCE_SCORING  ·  GPT-4o call #3  →  state = HITL_PENDING", C["agent"]["hi"], sz=8, w="bold", ha="center")
step_badge(step_x, ROW[r] + RH / 2, 5, C["agent"]["bd"])

box(1.2, ROW[r] + 0.1, 19.6, 0.72, "llm", lw=1.0, z=4, r=0.09)
conf_items = [
    ("Dot-notation keys", '"endpoints.0.path"'),
    ("Score  0-100",      "per field"),
    ("Status",            "HIGH · MEDIUM\nLOW · MISSING"),
    ("Suggestion",        "fix hint if low\nnull if high"),
    ("confidence_map",    "saved to DB\nHITL_PENDING set"),
]
cw = 3.7
for i, (label, detail) in enumerate(conf_items):
    cx = 1.4 + i * (cw + 0.06)
    txt(cx + cw / 2, ROW[r] + 0.64, label,  C["external"]["hi"], sz=6.8, w="bold")
    txt(cx + cw / 2, ROW[r] + 0.30, detail, MUTED,               sz=6,   mono=True)
llm_tag(18.9, ROW[r] + 0.62)
arrow(11.0, ROW[r], 11.0, ROW[r] - 0.28, C["frontend"]["bd"])

# ── Step 6 — HITL human review ────────────────────────────────────────────────
r = 5
box(1.0, ROW[r], 20.0, RH, "frontend", lw=1.6, z=2, r=0.18)
txt(11.0, ROW[r] + RH - 0.22, "FRONTEND  ·  HITL Validator  (/validate/:id)  —  Human Review", C["frontend"]["hi"], sz=8, w="bold", ha="center")
step_badge(step_x, ROW[r] + RH / 2, 6, C["frontend"]["bd"])

hitl_items = [
    ("Confidence dots", "GREEN ≥70\nYELLOW 40-69\nRED <40"),
    ("Editable fields", "click any field\nto override value"),
    ("Endpoint list",   "add / remove\nendpoints inline"),
    ("POST hitl",       "POST /api/agent/:id/hitl\nhuman_edits payload"),
    ("orchestrator", "_merge_edits()\ndraft + human_edits"),
]
hw = 3.7
for i, (label, detail) in enumerate(hitl_items):
    hx = 1.2 + i * (hw + 0.08)
    box(hx, ROW[r] + 0.1, hw, 0.72, "comp_fe", lw=0.7, z=4, r=0.09)
    txt(hx + hw / 2, ROW[r] + 0.62, label,  C["frontend"]["hi"], sz=7, w="bold")
    txt(hx + hw / 2, ROW[r] + 0.28, detail, MUTED,               sz=6)
arrow(11.0, ROW[r], 11.0, ROW[r] - 0.28, C["agent"]["bd"])

# ── Step 7 — Validator + ApiTestAgent + ApiSaver ──────────────────────────────
r = 6
box(1.0, ROW[r], 20.0, RH, "agent", lw=1.6, z=2, r=0.18)
txt(11.0, ROW[r] + RH - 0.22, "STAGE 6 + 7 + 8  ·  SchemaValidator → ApiTestAgent → ApiSaver", C["agent"]["hi"], sz=8, w="bold", ha="center")
step_badge(step_x, ROW[r] + RH / 2, 7, C["agent"]["bd"])

pipeline = [
    ("SchemaValidator", "Rule-based checks\nname/url/paths/methods", False),
    ("ApiTestAgent",    "GET-only live tests\nhttpx + GPT-4o #4 assess", True),
    ("encrypt_creds()", "Fernet encrypt\nauthentication stored", False),
    ("ApiSaver",        "ApiDefinition +\nApiEndpoint rows → DB", False),
    ("state=SAVED",     "Session finalized\nresult_id returned", False),
]
pw = 3.7
for i, (label, detail, is_llm) in enumerate(pipeline):
    px = 1.2 + i * (pw + 0.08)
    key = "llm" if is_llm else "comp_ag"
    box(px, ROW[r] + 0.1, pw, 0.72, key, lw=0.7, z=4, r=0.09)
    txt(px + pw / 2, ROW[r] + 0.62, label,  C["agent"]["hi"], sz=7, w="bold")
    txt(px + pw / 2, ROW[r] + 0.28, detail, MUTED,            sz=6)
    if is_llm:
        llm_tag(px + pw - 1.35, ROW[r] + 0.62)
    if i < len(pipeline) - 1:
        ax.annotate("", xy=(px + pw + 0.08, ROW[r] + 0.46),
                    xytext=(px + pw, ROW[r] + 0.46),
                    arrowprops=dict(arrowstyle="->", color=C["agent"]["lo"], lw=0.7),
                    zorder=7, annotation_clip=False)
arrow(11.0, ROW[r], 11.0, ROW[r] - 0.28, C["db"]["bd"])

# ── Step 8 — Database ─────────────────────────────────────────────────────────
r = 7
box(1.0, ROW[r], 20.0, RH - 0.1, "db", lw=1.6, z=2, r=0.18)
txt(11.0, ROW[r] + RH - 0.22, "DATABASE  ·  PostgreSQL", C["db"]["hi"], sz=8, w="bold", ha="center")
step_badge(step_x, ROW[r] + (RH - 0.1) / 2, 8, C["db"]["bd"])

db_tables = [
    ("api_definitions",  "name · base_url · tags\nvisibility · user_id"),
    ("api_endpoints",    "path · method · input_schema\nauth_credentials (encrypted)"),
    ("agent_sessions",   "state=SAVED · draft_api\nconfidence_map · final_api"),
]
dw = 6.0
for i, (label, detail) in enumerate(db_tables):
    dx = 1.2 + i * (dw + 0.2)
    box(dx, ROW[r] + 0.1, dw, 0.72, "comp_db", lw=0.7, z=4, r=0.09)
    txt(dx + dw / 2, ROW[r] + 0.58, label,  C["db"]["hi"], sz=7.5, w="bold", mono=True)
    txt(dx + dw / 2, ROW[r] + 0.26, detail, MUTED,         sz=6.2)

# ── Footer ─────────────────────────────────────────────────────────────────────
hline(0.68)
txt(0.6,  0.50, "MCP Hub  ·  Use Case 2  ·  Doc Upload uses 3-4 GPT-4o calls for full AI extraction", DIM, sz=6.5, ha="left")
txt(W - 0.6, 0.50, "LLM stages highlighted in amber", DIM, sz=6.5, ha="right")

out = os.path.join(os.path.dirname(__file__), "usecase2_doc_upload.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG, edgecolor="none")
plt.close()
print(f"Saved: {out}")
