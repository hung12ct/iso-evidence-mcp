# iso-evidence-mcp

Collect audit evidence without the busywork. Tell Claude Code what control you're working on, and it will:

**read the task from Notion → screenshot the proof on GitHub → upload it back to the Notion page.**

Built for ISO 27001, but works for any "do it, prove it, file it" task.

## 1. Install

In Claude Code:

```
/plugin marketplace add hung12ct/iso-evidence-mcp
/plugin install iso-evidence@iso-evidence-official
```

Run `/mcp` — you should see **iso-evidence** connected.

## 2. Set up (once)

```bash
# a) install uv (runs the server)
curl -LsSf https://astral.sh/uv/install.sh | sh

# b) add your Notion token (see "Get a Notion token" below)
export NOTION_TOKEN=ntn_xxx          # add to ~/.zshrc to keep it

# c) log in to GitHub once (saves the session for screenshots)
uvx --from git+https://github.com/hung12ct/iso-evidence-mcp.git iso-evidence login
```

## 3. Use

Just ask Claude Code:

> "Read the A.8.29 task from `<notion-url>`, screenshot the Unit Tests Actions run and the PR checks, and attach them to that page."

That's it.

---

### Get a Notion token

1. Go to <https://www.notion.so/my-integrations> → **New integration** → enable **Read** + **Insert content**.
2. Copy the secret (`ntn_…`) into `NOTION_TOKEN`.
3. Open your Notion page → **•••** → **Connections** → add the integration. *(Skip this and you'll get a 404.)*

> **Only a guest in the workspace?** Creating/installing an integration is a workspace **member/admin** action — guests usually can't do steps 1–3. Either ask a workspace admin to create the integration and share the pages (then use the token above), or read/write the pages through a connector that logs in **as you** (e.g. Claude Code's built-in `claude.ai Notion` connector via `/mcp`), which uses your own page permissions.

### Tools (what Claude uses under the hood)

| Tool | Does |
|---|---|
| `notion_get_task(page)` | Read the task page |
| `github_screenshot(url)` | Screenshot a logged-in GitHub page |
| `notion_attach_evidence(page, images)` | Upload screenshots back to the page |

### License

MIT.
