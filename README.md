# iso-evidence-mcp

Turn a repetitive audit chore into one agent loop:

> **read a task from Notion → (agent does the work in GitHub) → screenshot the proof → upload it back to the Notion page.**

A Claude Code plugin / MCP server. Built for ISO 27001 evidence gathering, but works for any "do it, prove it, file it" workflow.

| Tool | Purpose |
|---|---|
| `notion_get_task(page)` | Read a Notion page (title, properties, body) — e.g. an ISO control and the evidence it needs. |
| `github_screenshot(url, output_path?, selector?)` | Capture a screenshot of an **authenticated** GitHub page (Actions run, PR checks, file tree…). |
| `notion_attach_evidence(page, images, captions?)` | Upload the screenshots back onto the page as captioned image blocks. |

The agent (Claude Code) does the actual GitHub implementation; this server is the read/capture/upload glue.

---

## Install (Claude Code plugin)

```
/plugin marketplace add hung12ct/iso-evidence-mcp
/plugin install iso-evidence@iso-evidence-official
```

Run `/mcp` to confirm the **iso-evidence** server is connected.

### One-time setup

The plugin runs the server via `uvx` straight from this repo, so you need:

1. **[uv](https://docs.astral.sh/uv/)** installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. **`NOTION_TOKEN`** exported in your shell (see [Notion setup](#notion-setup)):
   ```bash
   export NOTION_TOKEN=ntn_xxx        # add to ~/.zshrc to persist
   ```
3. **GitHub login** captured once (saves a browser session for screenshots):
   ```bash
   uvx --from git+https://github.com/hung12ct/iso-evidence-mcp.git iso-evidence login
   ```

Chromium is downloaded automatically on first capture.

---

## Use it

Once connected, just ask Claude Code:

> "Read the A.8.29 task from `<notion-url>`, capture the Unit Tests Actions run and the PR checks, then attach them to that page with captions."

The agent calls `notion_get_task` → does/verifies the work → `github_screenshot` (one per shot) → `notion_attach_evidence`.

---

## Notion setup

1. Create an **internal integration**: <https://www.notion.so/my-integrations> — enable **Read content** and **Insert content**.
2. Copy the **Internal Integration Secret** (`ntn_…`) into `NOTION_TOKEN`.
3. **Share the target page** with the integration: open the page → **•••** → **Connections** → add your integration. *(Without this, the API returns 404 even with a valid token.)*

---

## Why Playwright + a saved session

GitHub Actions runs and PR checks are private pages — a headless browser must be logged in. You log in **once** in a real browser; the session (cookies) is saved to disk and reused headlessly for every later capture. No tokens end up in screenshots, no re-login.

---

## Alternatives

### Standalone CLI

```bash
uvx --from git+https://github.com/hung12ct/iso-evidence-mcp.git iso-evidence login
uvx --from git+https://github.com/hung12ct/iso-evidence-mcp.git \
  iso-evidence screenshot "https://github.com/OWNER/REPO/actions/runs/123" -o run.png
```

### Manual MCP config (no plugin)

Add to `~/.claude.json` or a project `.mcp.json`:

```json
{
  "mcpServers": {
    "iso-evidence": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/hung12ct/iso-evidence-mcp.git", "iso-evidence-mcp"],
      "env": { "NOTION_TOKEN": "ntn_xxx" }
    }
  }
}
```

### From a local clone (development)

```bash
pip install -e .
playwright install chromium
cp .env.example .env        # set NOTION_TOKEN
iso-evidence login
iso-evidence-mcp            # run the server
```

---

## Customize

Small, single-purpose modules under `src/iso_evidence_mcp/`:

- `screenshot.py` — Playwright capture + login session (viewport, full-page, selectors, wait, auto Chromium install).
- `notion.py` — Notion read + File Upload API (swap for another tracker by reimplementing two methods).
- `server.py` — the three MCP tools.
- `cli.py` — `login` / `screenshot` commands.

Plugin manifests live in `.claude-plugin/marketplace.json` and `plugins/iso-evidence/.claude-plugin/plugin.json`.

---

## License

MIT.
