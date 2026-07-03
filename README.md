# ✳ usage-island

Um app de **barra de menu** pra macOS que mostra o quanto você já usou do **Claude Code** — a janela de **5h** (atual) e a de **7d** (semana) — sempre à vista, sem precisar rodar `/usage`.

Inspirado no [Pookify](https://github.com/eyadhammouda/pookify), mas na menu bar e focado em **uso/cota** em vez de status de sessão.

```
✳ 49·13%                       ← barra de menu (5h · 7d)
┌──────────────────────────────┐
│ Plano (oficial · /usage)       │
│ ──────────────────────────     │
│ 5h (atual):  ████░░░░  49%     │
│      reseta em 2h31m           │
│ 7d (semana): █░░░░░░░  13%     │
│ ──────────────────────────     │
│ Atualizar agora                │
│ Sair                           │
└──────────────────────────────┘
```

## Como funciona

Duas fontes, nesta ordem:

1. **Plano (oficial).** Faz um probe minúsculo na Messages API da Anthropic e lê os headers `anthropic-ratelimit-unified-5h/7d-utilization` — **o mesmo número que o `/usage` mostra**. Precisa de um token do Claude Code.
2. **ccusage (fallback).** Se não houver token, cai pro [`ccusage`](https://github.com/ryoppippi/ccusage), que lê os logs locais em `~/.claude/projects/` e mostra **custo estimado em $** da janela de 5h e da semana.

> O probe usa `claude-haiku-4-5`, `max_tokens: 1` — consome uma fração ínfima da sua cota. Ele roda a cada 2 min (configurável). Nada sai da sua máquina além dessa chamada à própria API da Anthropic.

## Requisitos

- macOS (a barra de menu é via `rumps`/AppKit)
- Python 3
- Um token do Claude Code — pro % oficial (recomendado)
- `node`/`bun` no PATH — só se você for usar o modo ccusage (fallback)

## Instalação

```bash
git clone https://github.com/dougzeu/usage-island.git
cd usage-island
./install.sh
```

Depois pegue seu token do Claude Code e salve em `.token`:

```bash
claude setup-token          # gera um token OAuth (sk-ant-oat01-...)
# cole a saída no arquivo .token:
pbpaste > .token            # ou abra o arquivo e cole na mão
```

Rodar:

```bash
.venv/bin/python usage_island.py
```

O ✳ aparece na barra de menu. Clique pra ver os detalhes.

### Onde ele procura o token

Na ordem: variável de ambiente `CLAUDE_CODE_TOKEN` → arquivo `.token` → (fallback pessoal do autor, ignore). Cada pessoa usa o **próprio** token — ele fica só na sua máquina e **nunca** vai pro git (`.token` está no `.gitignore`).

## Abrir sozinho no login

Cria um LaunchAgent apontando pro seu venv. O `KeepAlive` com `SuccessfulExit=false`
faz o app **relançar se crashar**, mas respeitar quando você clica **Sair** no menu.

```bash
DIR="$(pwd)"
cat > ~/Library/LaunchAgents/com.usageisland.plist <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.usageisland</string>
  <key>ProgramArguments</key>
  <array><string>$DIR/.venv/bin/python</string><string>$DIR/usage_island.py</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <key>StandardOutPath</key><string>$DIR/island.log</string>
  <key>StandardErrorPath</key><string>$DIR/island.log</string>
</dict></plist>
PLIST
launchctl load -w ~/Library/LaunchAgents/com.usageisland.plist
```

| Ação | Comando |
|---|---|
| Reabrir depois de clicar "Sair" | `launchctl start com.usageisland` |
| Desligar de vez (não abrir no login) | `launchctl unload ~/Library/LaunchAgents/com.usageisland.plist` |
| Religar | `launchctl load -w ~/Library/LaunchAgents/com.usageisland.plist` |

## Configuração

No topo do `usage_island.py`:

| Constante | O que é |
|---|---|
| `REFRESH_SECONDS` | intervalo de atualização (padrão 120s) |
| `WEEKLY_LIMIT_USD` | teto em $ usado **só** no modo ccusage (fallback), pra virar barra de % |
| `ICON` | o `✳`. Pra ter o laranja de verdade, troque por um PNG template (comentado no código) |

## Verificar sem GUI

```bash
.venv/bin/python usage_island.py --check
```

Imprime o que cada fonte retorna e qual está ativa.

## Créditos

- Técnica do probe de rate limit: reaproveitada de um projeto meu de hardware (medidor de cota num display físico ESP8266).
- Ideia da "ilha" de status: [Pookify](https://github.com/eyadhammouda/pookify).
- Fallback de custo: [ccusage](https://github.com/ryoppippi/ccusage).

## Aviso

A API de rate limit **não é documentada** — nomes de header e versão do beta podem mudar sem aviso. Se um dia parar, o app cai pro ccusage sozinho; é só atualizar os nomes dos headers no código.

MIT. Sem garantias, sem coleta de dados.
