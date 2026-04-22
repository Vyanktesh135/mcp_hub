"""
MCP Hub — Professional System Architecture Diagram
Renders to: Docs/images/01_system_architecture.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

# ── Canvas ─────────────────────────────────────────────────────────────────────
W, H = 24, 17
BG = "#f6f8fa"

# ── Palette ────────────────────────────────────────────────────────────────────
C = {
    "user":     {"bg": "#ffffff", "bd": "#94a3b8", "hi": "#1e293b", "lo": "#64748b"},
    "frontend": {"bg": "#eff6ff", "bd": "#3b82f6", "hi": "#1d4ed8", "lo": "#2563eb"},
    "backend":  {"bg": "#f0fdf4", "bd": "#16a34a", "hi": "#14532d", "lo": "#166534"},
    "agent":    {"bg": "#f5f3ff", "bd": "#7c3aed", "hi": "#4c1d95", "lo": "#6d28d9"},
    "utils":    {"bg": "#fff1f2", "bd": "#e11d48", "hi": "#881337", "lo": "#be123c"},
    "external": {"bg": "#fffbeb", "bd": "#d97706", "hi": "#78350f", "lo": "#92400e"},
    "db":       {"bg": "#f0f9ff", "bd": "#0284c7", "hi": "#0c4a6e", "lo": "#0369a1"},
    "mw":       {"bg": "#dcfce7", "bd": "#16a34a", "hi": "#14532d", "lo": "#166534"},
    "comp_fe":  {"bg": "#dbeafe", "bd": "#93c5fd", "hi": "#1e40af", "lo": "#2563eb"},
    "comp_be":  {"bg": "#dcfce7", "bd": "#86efac", "hi": "#14532d", "lo": "#15803d"},
    "comp_ag":  {"bg": "#ede9fe", "bd": "#c4b5fd", "hi": "#3b0764", "lo": "#6d28d9"},
    "comp_ext": {"bg": "#fef3c7", "bd": "#fcd34d", "hi": "#451a03", "lo": "#92400e"},
    "comp_db":  {"bg": "#e0f2fe", "bd": "#7dd3fc", "hi": "#0c4a6e", "lo": "#0369a1"},
    "comp":     {"bg": "#f8fafc", "bd": "#cbd5e1", "hi": "#1e293b", "lo": "#64748b"},
    "llm_tag":  {"bg": "#fef3c7", "bd": "#f59e0b", "hi": "#78350f", "lo": "#92400e"},
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

# ── Helpers ────────────────────────────────────────────────────────────────────

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

def section_label(x, y, w, h, key, title, subtitle=""):
    txt(x + 0.35, y + h - 0.32, title,
        C[key]["hi"], sz=8.5, w="bold", ha="left", z=8)
    if subtitle:
        txt(x + len(title) * 0.20 + 0.55, y + h - 0.32, subtitle,
            C[key]["lo"], sz=7.5, ha="left", z=8)

def arrow(x1, y1, x2, y2, color=DIM, lw=1.3, style="->", dash=False):
    props = dict(arrowstyle=style, color=color, lw=lw, mutation_scale=10)
    if dash:
        props["linestyle"] = "dashed"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=props, zorder=6, annotation_clip=False)

def hline(y, color="#cbd5e1", lw=0.8):
    ax.plot([0.5, W - 0.5], [y, y], color=color, lw=lw, zorder=1)


# ══════════════════════════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════════════════════════
txt(W / 2, 16.55, "MCP HUB", TEXT, sz=24, w="bold", mono=True)
txt(W / 2, 16.10, "System Architecture", MUTED, sz=12)
hline(15.80)

# ══════════════════════════════════════════════════════════════════════════════
# USER
# ══════════════════════════════════════════════════════════════════════════════
bx, by, bw, bh = 9.0, 14.88, 6.0, 0.72
box(bx, by, bw, bh, "user", lw=1.0, z=3, r=0.12)
txt(bx + bw / 2, by + 0.48, "Browser / User", C["user"]["hi"], sz=9, w="bold")
txt(bx + bw / 2, by + 0.22, "Initiates all interactions via React SPA", C["user"]["lo"], sz=7)

arrow(12, by, 12, by - 0.38, DIM)
txt(12.3, by - 0.18, "HTTPS", DIM, sz=5.5, ha="left")

# ══════════════════════════════════════════════════════════════════════════════
# FRONTEND
# ══════════════════════════════════════════════════════════════════════════════
fx, fy, fw, fh = 0.4, 12.2, 23.2, 2.45
box(fx, fy, fw, fh, "frontend", lw=1.8, z=2, r=0.22)
section_label(fx, fy, fw, fh, "frontend", "FRONTEND", "·  React + Vite  ·  localhost:5173")

pages = [
    ("Auth Pages",       "/login  ·  /register"),
    ("Chat Builder",     "/create/chat"),
    ("Doc Upload",       "/create/upload"),
    ("HITL Validator",   "/validate/:id"),
    ("Registry",         "/registry"),
    ("ChatGPT Hub",      "/chatgpt"),
    ("Monitor",          "/monitor"),
    ("Admin",            "/admin"),
]
pw, ph = 2.72, 0.72
pgap  = (fw - 0.3 - pw * 8) / 7
py1   = fy + fh - 1.12
for i, (name, path) in enumerate(pages):
    px = fx + 0.15 + i * (pw + pgap)
    box(px, py1, pw, ph, "comp_fe", lw=0.8, z=4, r=0.1)
    txt(px + pw / 2, py1 + ph * 0.66, name,  "#1e3a5f", sz=7.5, w="bold")
    txt(px + pw / 2, py1 + ph * 0.28, path,  DIM,       sz=6.5, mono=True)

# Context bar
ctx_items = [
    ("AuthContext",     "JWT · user · role"),
    ("LanguageContext", "EN / JA  i18n"),
    ("ThemeContext",    "dark / light"),
    ("lib/api.js",      "Axios + JWT Bearer interceptor"),
]
ciw = (fw - 0.3 - 0.15 * 3) / 4
for i, (n, d) in enumerate(ctx_items):
    cix = fx + 0.15 + i * (ciw + 0.15)
    box(cix, fy + 0.1, ciw, 0.5, "frontend", lw=0.5, z=4, r=0.07)
    txt(cix + 0.2, fy + 0.38, n, C["frontend"]["hi"], sz=7,   w="bold", ha="left")
    txt(cix + 0.2, fy + 0.18, d, DIM,                sz=6.5,            ha="left")

arrow(12, fy, 12, fy - 0.32, C["frontend"]["bd"])
txt(12.3, fy - 0.15, "REST + JWT Bearer", DIM, sz=5.5, ha="left")

# ══════════════════════════════════════════════════════════════════════════════
# BACKEND
# ══════════════════════════════════════════════════════════════════════════════
bkx, bky, bkw, bkh = 0.4, 9.85, 23.2, 2.25
box(bkx, bky, bkw, bkh, "backend", lw=1.8, z=2, r=0.22)
section_label(bkx, bky, bkw, bkh, "backend", "BACKEND", "·  FastAPI  ·  localhost:8000")

# Middleware banner
box(bkx + 0.15, bky + bkh - 0.72, bkw - 0.3, 0.44, "mw", lw=0.6, z=4, r=0.08)
mws = ["CORS Middleware", "SlowAPI Rate Limiting  (5–60 req/min)", "JWT Auth Guard", "Global Exception Handlers"]
mw_w = (bkw - 0.3) / len(mws)
for i, m in enumerate(mws):
    txt(bkx + 0.15 + (i + 0.5) * mw_w, bky + bkh - 0.50, m, C["backend"]["hi"], sz=7, w="bold")

# Router boxes
routers = [
    ("/api/auth",    "register · login · me\nadmin user management"),
    ("/api/agent",   "chat · upload · manual\nhitl · confirm · list"),
    ("/api/registry","list · get\ndelete"),
    ("/api/chatgpt", "stats · connect · disconnect\nchat with GPT-4o tools"),
    ("/api/monitor", "overview · active\nsessions · tool-calls"),
]
rw2 = (bkw - 0.3 - 0.2 * 4) / 5
for i, (route, desc) in enumerate(routers):
    rx2 = bkx + 0.15 + i * (rw2 + 0.2)
    box(rx2, bky + 0.14, rw2, 1.1, "comp_be", lw=0.9, z=4, r=0.1)
    txt(rx2 + rw2 / 2, bky + 0.14 + 0.80, route, C["backend"]["hi"], sz=7.5, w="bold", mono=True)
    txt(rx2 + rw2 / 2, bky + 0.14 + 0.40, desc,  MUTED,              sz=6.5)

# Arrows leaving backend
for ax_x in [5.5, 12.0, 16.0, 21.5]:
    arrow(ax_x, bky, ax_x, bky - 0.30, C["backend"]["bd"])

# ══════════════════════════════════════════════════════════════════════════════
# AGENT PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
apx, apy, apw, aph = 0.4, 5.7, 13.8, 3.9
box(apx, apy, apw, aph, "agent", lw=1.8, z=2, r=0.22)
section_label(apx, apy, apw, aph, "agent", "AGENT PIPELINE", "·  Orchestrator  ·  8-stage state machine")

stages = [
    ("①", "CLASSIFY",   "InputClassifier",   False),
    ("②", "PARSE",      "ParsingAgent",      False),
    ("③", "SCHEMA",     "SchemaAgent",       True),
    ("④", "CONFIDENCE", "ConfidenceAgent",   True),
    ("⑤", "HITL",       "Human Review",      False),
    ("⑥", "VALIDATE",   "SchemaValidator",   False),
    ("⑦", "TEST",       "ApiTestAgent",      False),
    ("⑧", "SAVE",       "ApiSaver",          False),
]
stw = (apw - 0.3 - 0.12 * 7) / 8
sth = 2.2
sty = apy + 0.52
for i, (num, name, cls, is_llm) in enumerate(stages):
    sx = apx + 0.15 + i * (stw + 0.12)
    key = "llm_tag" if is_llm else "comp_ag"
    box(sx, sty, stw, sth, key, lw=0.9, z=4, r=0.1)
    txt(sx + stw / 2, sty + sth * 0.88, num,  C["agent"]["hi"], sz=10,  w="bold")
    txt(sx + stw / 2, sty + sth * 0.62, name, C["agent"]["hi"], sz=7,   w="bold")
    txt(sx + stw / 2, sty + sth * 0.38, cls,  MUTED,            sz=6)
    if is_llm:
        box(sx + stw * 0.12, sty + 0.1, stw * 0.76, 0.44, "external", lw=0.5, z=5, r=0.07)
        txt(sx + stw / 2, sty + 0.32, "GPT-4o", C["external"]["hi"], sz=6.5, w="bold")
    if i < len(stages) - 1:
        ax.annotate("", xy=(sx + stw + 0.12, sty + sth / 2),
                    xytext=(sx + stw, sty + sth / 2),
                    arrowprops=dict(arrowstyle="->", color=C["agent"]["lo"], lw=0.7),
                    zorder=7, annotation_clip=False)

# ══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
utx, uty, utw, uth = 14.5, 5.7, 4.0, 3.9
box(utx, uty, utw, uth, "utils", lw=1.8, z=2, r=0.22)
section_label(utx, uty, utw, uth, "utils", "UTILITIES", "")

util_items = [
    ("auth.py",        "JWT creation · bcrypt verify\nrequire_admin dependency"),
    ("encryption.py",  "Fernet symmetric encrypt\nSHA-256 key derivation"),
    ("limiter.py",     "SlowAPI instance\nper-route rate limits"),
    ("translator.py",  "api_to_tools()\nresolve_tool_call()"),
]
uiw = utw - 0.4
uih = 0.74
for i, (n, d) in enumerate(util_items):
    uiy = uty + uth - 0.88 - i * (uih + 0.12)
    box(utx + 0.2, uiy, uiw, uih, "comp", lw=0.6, z=4, r=0.09)
    txt(utx + 0.38, uiy + uih * 0.72, n, C["utils"]["hi"], sz=7,   w="bold", ha="left", mono=True)
    txt(utx + 0.38, uiy + uih * 0.32, d, MUTED,            sz=6.2,            ha="left")

# ══════════════════════════════════════════════════════════════════════════════
# EXTERNAL SERVICES
# ══════════════════════════════════════════════════════════════════════════════
ex, ey, ew, eh = 18.8, 5.7, 4.8, 3.9
box(ex, ey, ew, eh, "external", lw=1.8, z=2, r=0.22)
section_label(ex, ey, ew, eh, "external", "EXTERNAL SERVICES", "")

# OpenAI
box(ex + 0.2, ey + 1.85, ew - 0.4, 1.78, "comp_ext", lw=0.8, z=4, r=0.12)
txt(ex + ew / 2, ey + 3.30, "OpenAI  —  GPT-4o", C["external"]["hi"], sz=8.5, w="bold")
for j, line in enumerate(["Schema Generation  (stage 3)", "Confidence Scoring  (stage 4)", "Agentic Chat loop"]):
    txt(ex + ew / 2, ey + 3.0 - j * 0.32, line, MUTED, sz=6.5)

# External APIs
box(ex + 0.2, ey + 0.18, ew - 0.4, 1.5, "comp_ext", lw=0.8, z=4, r=0.12)
txt(ex + ew / 2, ey + 1.38, "External REST APIs", C["external"]["hi"], sz=8.5, w="bold")
for j, line in enumerate(["Tool execution targets", "HTTP via httpx  ·  verify=False", "Basic / Bearer / API Key auth"]):
    txt(ex + ew / 2, ey + 1.05 - j * 0.30, line, MUTED, sz=6.5)

# Dashed connectors: Agent/chatgpt → External
arrow(14.5, 8.1, 18.8, 7.8, C["external"]["lo"], lw=1.0, dash=True)
txt(16.65, 8.15, "LLM calls", C["external"]["lo"], sz=5.5)
arrow(14.5, 7.1, 18.8, 6.6, C["external"]["lo"], lw=1.0, dash=True)
txt(16.65, 7.05, "HTTP tool calls", C["external"]["lo"], sz=5.5)

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════════════════════
dbx, dby, dbw, dbh = 0.4, 3.0, 23.2, 2.5
box(dbx, dby, dbw, dbh, "db", lw=1.8, z=2, r=0.22)
section_label(dbx, dby, dbw, dbh, "db", "DATABASE", "·  PostgreSQL  ·  SQLite (local dev)")

tables = [
    ("users",                "id · email · hashed_password\nrole · is_active · created_at"),
    ("agent_sessions",       "state · draft_api · confidence_map\nhuman_edits · final_api · user_id"),
    ("api_definitions",      "name · base_url · version\nvisibility · user_id · tags"),
    ("api_endpoints",        "path · method · input_schema\noutput_schema · auth_credentials"),
    ("chatgpt_connections",  "api_definition_id · user_id\nconnected_at · is_active"),
    ("tool_call_logs",       "endpoint_name · arguments\nresult · success · called_at"),
]
dtw = (dbw - 0.3 - 0.2 * 5) / 6
for i, (n, d) in enumerate(tables):
    dx = dbx + 0.15 + i * (dtw + 0.2)
    box(dx, dby + 0.15, dtw, 2.1, "comp_db", lw=0.8, z=4, r=0.1)
    txt(dx + dtw / 2, dby + 0.15 + 1.76, n, C["db"]["hi"], sz=7.5, w="bold", mono=True)
    txt(dx + dtw / 2, dby + 0.15 + 1.0,  d, MUTED,         sz=6.2)

# Arrows into DB
for ax_x in [5.5, 12.0, 16.0]:
    arrow(ax_x, apy, ax_x, dby + 2.3, C["db"]["bd"])

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
hline(2.78)
txt(0.6,  2.58, "MCP Hub  ·  FastAPI + React + PostgreSQL + GPT-4o", DIM, sz=7, ha="left")
txt(W - 0.6, 2.58, "System Architecture  v1.0", DIM, sz=7, ha="right")

# ── Save ───────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "01_system_architecture.png")
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG, edgecolor="none")
plt.close()
print(f"Saved: {out}")
