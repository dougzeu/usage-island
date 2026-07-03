#!/usr/bin/env bash
# Setup do usage-island: cria o venv, instala o rumps e explica o token.
set -e
cd "$(dirname "$0")"

echo "→ criando venv e instalando dependências..."
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt

if [ ! -f .token ]; then
  echo
  echo "→ falta o token do Claude Code (pra mostrar o % OFICIAL do plano)."
  echo "  1. rode:   claude setup-token"
  echo "  2. cole a saída (sk-ant-oat01-...) em:  $(pwd)/.token"
  echo
  echo "  Sem token, o app roda mesmo assim no modo ccusage (custo estimado em \$)."
fi

echo
echo "✓ pronto. Pra rodar:"
echo "    .venv/bin/python usage_island.py"
