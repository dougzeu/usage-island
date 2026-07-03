#!/usr/bin/env bash
# dd-claudeusage — instalador de uma linha:
#   curl -fsSL https://raw.githubusercontent.com/dougzeu/dd-claudeusage/main/bootstrap.sh | bash
set -e
REPO="dougzeu/dd-claudeusage"
DEST="$HOME/dd-claudeusage"
PL="$HOME/Library/LaunchAgents/com.dd-claudeusage.plist"
say() { printf '\n\033[1m%s\033[0m\n' "$*"; }

say "dd-claudeusage — instalador"

# 1) Python 3 (o app usa rumps) ------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  say "Falta o Python 3 — vou abrir a instalação do Command Line Tools da Apple."
  echo "  → Clique \"Instalar\" na janela que aparecer e espere terminar."
  xcode-select --install 2>/dev/null || true
  echo "  → Quando terminar, rode este instalador de novo."
  exit 1
fi

# 2) Claude Code — OBRIGATÓRIO -------------------------------------------------
# (o app mede o uso do Claude Code; sem ele não há token nem dados)
export PATH="$HOME/.local/bin:$PATH"
if ! command -v claude >/dev/null 2>&1; then
  say "Claude Code não encontrado — instalando (necessário)…"
  curl -fsSL https://claude.ai/install.sh | bash
  export PATH="$HOME/.local/bin:$PATH"
  if ! command -v claude >/dev/null 2>&1; then
    say "Claude Code instalado, mas não está no PATH desta sessão."
    echo "  → Feche e reabra o Terminal e rode este instalador de novo."
    exit 1
  fi
fi
echo "✓ Claude Code $(claude --version 2>/dev/null | awk '{print $1}')"

# 3) baixar o projeto (tarball — sem precisar de git) --------------------------
say "Baixando o dd-claudeusage…"
TOKEN_BAK=""
[ -f "$DEST/.token" ] && TOKEN_BAK="$(cat "$DEST/.token")"   # preserva token numa reinstalação
TMP="$(mktemp -d)"
curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" | tar xz -C "$TMP"
rm -rf "$DEST"
mv "$TMP/dd-claudeusage-main" "$DEST"
rm -rf "$TMP"
[ -n "$TOKEN_BAK" ] && printf '%s' "$TOKEN_BAK" > "$DEST/.token"

# 4) setup (venv, app da barra, LaunchAgent) ----------------------------------
say "Instalando o app…"
cd "$DEST"
chmod +x install.sh
./install.sh

# 5) token — o % OFICIAL do plano ---------------------------------------------
if [ ! -f "$DEST/.token" ]; then
  say "Último passo: o token (mostra o % OFICIAL do plano, igual ao /usage)"
  echo "Vou rodar 'claude setup-token'. Uma janela do navegador vai abrir:"
  echo "  1. faça login / autorize o acesso"
  echo "  2. o comando imprime um token começando com  sk-ant-oat01-..."
  echo
  claude setup-token </dev/tty >/dev/tty 2>&1 || true
  echo
  echo "Cole o token aqui e tecle Enter (ou só Enter pra pular → modo custo estimado):"
  read -r TOK </dev/tty || TOK=""
  if [ -n "$TOK" ]; then
    printf '%s' "$TOK" > "$DEST/.token"
    launchctl unload "$PL" 2>/dev/null || true
    launchctl load -w "$PL"
    echo "✓ token salvo — mostrando o % do plano."
  else
    echo "→ sem token: modo custo estimado (\$). Pra ativar depois, cole o token em $DEST/.token"
  fi
fi

say "✓ Pronto! Procure 'dd-claudeusage' no Spotlight (Cmd+Espaço)."
