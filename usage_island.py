#!/usr/bin/env python3
"""usage-island — menubar app (macOS) com usage do Claude Code: janela 5h + 7d.

Inspirado no Pookify, mas na barra de menu e focado em USAGE.

Duas fontes, nesta ordem:
  1. PLANO (oficial) — probe mínimo na Messages API só pra ler os headers
     `anthropic-ratelimit-unified-5h/7d-utilization` (o mesmo número do /usage).
     Técnica reaproveitada do projeto ~/Projects/nodemcu/tokenmeter.
  2. ccusage (fallback) — custo/tokens locais de ~/.claude/projects, se o probe falhar.

Uso:
    python usage_island.py            # roda o app na barra de menu
    python usage_island.py --check    # valida as duas fontes sem abrir GUI
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

# --- Fonte 1: plano (oficial) ------------------------------------------------
CLAUDE_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # probe barato; max_tokens=1
H_5H = "anthropic-ratelimit-unified-5h-utilization"
H_7D = "anthropic-ratelimit-unified-7d-utilization"
H_5H_RESET = "anthropic-ratelimit-unified-5h-reset"
TOKEN_FILE = os.path.expanduser("~/usage-island/.token")
TOKENMETER_CONFIG = os.path.expanduser("~/Projects/nodemcu/tokenmeter/config.h")

# --- Fonte 2: ccusage (fallback) — teto configurável, só usado sem token -----
# ponytail: só entra em ação se o probe do plano falhar; aí não temos % oficial,
# então mostramos custo $ contra este teto. Ajuste ao seu plano.
WEEKLY_LIMIT_USD = 200.0

# ponytail: probe a cada 120s. As janelas 5h/7d andam devagar e o probe consome
# uma fração de cota (é haiku, max_tokens=1) — não vale medir de minuto em minuto.
REFRESH_SECONDS = 120
# ponytail: o logo do Claude não tem emoji unicode; ✳ (sunburst) é o mais próximo e
# monocromático (adapta a dark/light). Pra ter o laranja de verdade, troque por um
# PNG template: rumps.App(icon="claude.png", template=True) no lugar do título.
ICON = "✳"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _bar(pct, n=8):
    fill = round(pct / 100 * n)
    return "█" * fill + "░" * (n - fill)


def _countdown(epoch):
    if not epoch:
        return ""
    m = max(0, int((epoch - datetime.now(timezone.utc).timestamp()) // 60))
    return f"{m // 60}h{m % 60:02d}m"


def _fmt_tok(n):
    if n >= 1e9:
        return f"{n / 1e9:.1f}B"
    if n >= 1e6:
        return f"{n / 1e6:.1f}M"
    return f"{round(n / 1e3)}k"


# ---------------------------------------------------------------------------
# Fonte 1: plano (oficial)
# ---------------------------------------------------------------------------
def _claude_token():
    """Token OAuth do Claude Code. Env > ~/usage-island/.token > config.h do tokenmeter."""
    t = os.environ.get("CLAUDE_CODE_TOKEN")
    if t:
        return t.strip()
    if os.path.exists(TOKEN_FILE):
        t = open(TOKEN_FILE, encoding="utf-8").read().strip()
        if t:
            return t
    try:  # reusa o token do tokenmeter — fonte única, sem duplicar o segredo
        for line in open(TOKENMETER_CONFIG, encoding="utf-8"):
            if "CLAUDE_TOKEN" in line and '"' in line:
                return line.split('"')[1]
    except OSError:
        pass
    return None


def probe_plan():
    """POST mínimo na Messages API só pra ler os headers de rate limit. None se indisponível."""
    token = _claude_token()
    if not token:
        return None
    body = json.dumps({
        "model": CLAUDE_MODEL, "max_tokens": 1,
        "messages": [{"role": "user", "content": "."}],
    }).encode()
    req = urllib.request.Request(CLAUDE_URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "oauth-2025-04-20",
        "content-type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            h = r.headers
    except urllib.error.HTTPError as e:
        h = e.headers  # headers de ratelimit vêm mesmo em 429/4xx
    except (urllib.error.URLError, OSError):
        return None
    if h is None or h.get(H_5H) is None:
        return None

    def pct(name):
        v = h.get(name)
        return round(float(v) * 100) if v is not None else None

    reset = (h.get(H_5H_RESET) or "").strip()
    return {
        "src": "plan",
        "p5h": pct(H_5H),
        "p7d": pct(H_7D),
        "reset": _countdown(int(reset)) if reset.isdigit() else "",
    }


# ---------------------------------------------------------------------------
# Fonte 2: ccusage (fallback)
# ---------------------------------------------------------------------------
def _ccusage(*args):
    if shutil.which("ccusage"):
        base = ["ccusage"]
    elif shutil.which("bunx"):
        base = ["bunx", "ccusage@latest"]
    else:
        base = ["npx", "-y", "ccusage@latest"]
    r = subprocess.run(base + list(args) + ["--json"],
                       capture_output=True, text=True, timeout=120)
    i = r.stdout.find("{")
    if i < 0:
        raise RuntimeError(r.stderr.strip() or "ccusage não retornou JSON")
    return json.loads(r.stdout[i:])


def probe_ccusage():
    b = (_ccusage("blocks", "--active").get("blocks") or [{}])[0]
    reset = ""
    if b.get("endTime"):
        end = datetime.fromisoformat(b["endTime"].replace("Z", "+00:00"))
        reset = _countdown(end.timestamp())
    weeks = _ccusage("weekly").get("weekly") or []
    cur = max((e["period"] for e in weeks), default=None)
    wcost = 0.0
    wtok = 0
    for e in weeks:
        if e["period"] != cur:
            continue
        for mb in e.get("modelBreakdowns", []):
            if mb.get("modelName", "").startswith("claude"):
                wcost += mb.get("cost", 0)
                wtok += (mb.get("inputTokens", 0) + mb.get("outputTokens", 0)
                         + mb.get("cacheCreationTokens", 0) + mb.get("cacheReadTokens", 0))
    return {
        "src": "ccusage",
        "cur_cost": b.get("costUSD", 0.0), "cur_tok": b.get("totalTokens", 0),
        "reset": reset, "wcost": wcost, "wtok": wtok,
        "wpct": min(100, round(100 * wcost / WEEKLY_LIMIT_USD)) if WEEKLY_LIMIT_USD else 0,
    }


def collect():
    """Plano oficial se der; senão ccusage."""
    return probe_plan() or probe_ccusage()


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
def _run_gui():
    import rumps

    class UsageApp(rumps.App):
        def __init__(self):
            super().__init__(ICON, quit_button="Sair")
            self.head = rumps.MenuItem("")
            self.l1 = rumps.MenuItem("")
            self.l2 = rumps.MenuItem("")
            self.l3 = rumps.MenuItem("")
            self.l4 = rumps.MenuItem("")
            self.menu = [self.head, None, self.l1, self.l2, self.l3, self.l4, None,
                         rumps.MenuItem("Atualizar agora", callback=self.refresh)]
            self.timer = rumps.Timer(self.refresh, REFRESH_SECONDS)
            self.timer.start()
            self.refresh(None)

        def refresh(self, _):
            try:
                d = collect()
            except Exception as e:  # ponytail: qualquer falha vira aviso, não crash
                self.title = f"{ICON} ⚠︎"
                self.head.title = f"erro: {str(e)[:48]}"
                return
            if d["src"] == "plan":
                self._render_plan(d)
            else:
                self._render_ccusage(d)

        def _render_plan(self, d):
            p5h, p7d = d["p5h"], d["p7d"]
            self.title = f"{ICON} {p5h if p5h is not None else '—'}·{p7d if p7d is not None else '—'}%"
            self.head.title = "Plano (oficial · /usage)"
            reset = f"   reseta em {d['reset']}" if d["reset"] else ""
            self.l1.title = f"5h (atual):   {_bar(p5h or 0)}  {p5h if p5h is not None else '—'}%"
            self.l2.title = f"          {reset.strip()}" if d["reset"] else ""
            self.l3.title = f"7d (semana):  {_bar(p7d or 0)}  {p7d if p7d is not None else '—'}%"
            self.l4.title = ""

        def _render_ccusage(self, d):
            self.title = f"{ICON} {d['wpct']}%*"
            self.head.title = "ccusage (estimativa · sem token do plano)"
            self.l1.title = f"Bloco 5h:  ${d['cur_cost']:.2f}  ·  {_fmt_tok(d['cur_tok'])} tok"
            self.l2.title = f"          reseta em {d['reset']}" if d["reset"] else "sem bloco ativo"
            self.l3.title = f"Semana:  ${d['wcost']:.2f} / ${WEEKLY_LIMIT_USD:.0f}   {_bar(d['wpct'])} {d['wpct']}%"
            self.l4.title = f"          {_fmt_tok(d['wtok'])} tokens"

    UsageApp().run()


if __name__ == "__main__":
    if "--check" in sys.argv:
        plan = probe_plan()
        print("PLAN  :", json.dumps(plan) if plan else "indisponível (sem token / API off)")
        cc = probe_ccusage()
        assert cc["cur_cost"] >= 0 and cc["wcost"] >= 0, cc
        print("CCUSAGE:", json.dumps(cc, default=str))
        print("OK — fonte ativa:", collect()["src"])
    else:
        _run_gui()
