<img src="assets/appicon.png" width="112" align="right" alt="ícone">

<br><br>

# dd-claudeusage

Um app pra **Mac** que mostra, lá no topo da tela (na barra de menu), o quanto você já usou do **Claude Code** — a cota das **últimas 5 horas** e a da **semana**. Sempre à vista, sem precisar digitar `/usage`.

```
✳ 49·13%   ← fica aqui no topo (5h · 7d)
┌──────────────────────────────┐
│ 5h (agora):  ████░░░░  49%    │
│      reseta em 2h31m          │
│ 7d (semana): █░░░░░░░  13%    │
└──────────────────────────────┘
```

---

## Como instalar

### 1. Abra o Terminal

Aperte **Cmd + Espaço**, digite **Terminal** e tecle **Enter**.

### 2. Cole este comando e tecle Enter

```bash
curl -fsSL https://raw.githubusercontent.com/dougzeu/dd-claudeusage/main/bootstrap.sh | bash
```

### 3. Siga o que aparecer na tela

Pronto — quando terminar, o ícone **✳** aparece no topo da tela. Clique nele pra ver seus números.

---

## O que vai aparecer durante a instalação

O instalador faz tudo sozinho. Dependendo do seu Mac, pode aparecer:

**🪟 Uma janela da Apple pedindo pra instalar ferramentas**
→ Clique em **Instalar**, espere terminar e rode o comando do passo 2 **de novo**. (Só acontece se você ainda não tem o Python.)

**⏳ "Instalando Claude Code…"**
→ Não precisa fazer nada, ele instala sozinho. (O app precisa do Claude Code pra funcionar.)

**🌐 O navegador abre pedindo pra fazer login**
→ Faça login na sua conta Claude e clique em **autorizar**. Volte pro Terminal: vai aparecer um código começando com `sk-ant-oat01-...`. **Copie e cole** no Terminal e tecle Enter.
→ Isso liga o número **oficial** (o mesmo do `/usage`). Se preferir, só tecle **Enter** pra pular — o app funciona mesmo assim, mostrando o custo estimado em **$**.

---

## Depois de instalar

- **O ✳ some?** Ele fica no topo da tela, entre os outros ícones. Abre sozinho toda vez que você liga o Mac.
- **Fechei sem querer / quero reabrir:** aperte **Cmd + Espaço**, digite **dd-claudeusage** e tecle **Enter**.
- **Fechar:** clique no **✳** → **Sair**.

---

## Deu algum problema?

| Problema | O que fazer |
|---|---|
| Apareceu a janela de "instalar ferramentas" | Clique **Instalar**, espere, e rode o comando do passo 2 de novo |
| `curl: command not found` | Você não está no Terminal do Mac — repita o passo 1 |
| Não acho o ✳ no topo | Tente reabrir pelo Spotlight (Cmd+Espaço → `dd-claudeusage`) |
| Quero desinstalar | Apague a pasta `dd-claudeusage` na sua Home e o arquivo `~/Library/LaunchAgents/com.dd-claudeusage.plist` |

---

<sub>App de barra de menu pra macOS. Feito com Python + [rumps](https://github.com/jaredks/rumps). Seu token fica só na sua máquina. Licença MIT.</sub>
