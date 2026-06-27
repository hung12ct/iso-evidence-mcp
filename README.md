# iso-evidence-mcp

An MCP server that turns a repetitive audit chore into one agent loop:

> **read a task from Notion → (agent does the work in GitHub) → screenshot the proof → upload it back to the Notion page.**

Built for ISO 27001 evidence gathering, but works for any "do it, prove it, file it" workflow.

## What it gives the agent

| Tool | Purpose |
|---|---|
| `notion_get_task(page)` | Read a Notion page (title, properties, body) — e.g. an ISO control and the evidence it needs. |
| `github_screenshot(url, output_path?, selector?)` | Capture a screenshot of an **authenticated** GitHub page (Actions run, PR checks, file tree…). |
| `notion_attach_evidence(page, images, captions?)` | Upload the screenshots back onto the page as captioned image blocks. |

The agent (Claude Code, etc.) does the actual GitHub implementation; this server is the glue around it.

## Why Playwright + a saved session

GitHub Actions runs and PR checks are private pages — a headless browser needs to be logged in. You log in **once** in a real browser; the session (cookies) is saved to disk and reused headlessly for every later capture. No tokens in screenshots, no re-login.

## Install as a Claude Code plugin (easiest)

```
/plugin marketplace add hung12ct/iso-evidence-mcp
/plugin install iso-evidence@iso-evidence-official
```

Then run `/mcp` to confirm the **iso-evidence** server is connected.

The plugin runs the server via `uvx` from this repo, so you need **[uv](https://docs.astral.sh/uv/)** installed, `NOTION_TOKEN` exported in your shell, and a one-time GitHub login:

```bash
export NOTION_TOKEN=ntn_xxx
uvx --from git+https://github.com/hung12ct/iso-evidence-mcp.git iso-evidence login
```

Chromium is installed automatically on first capture. See
[`plugins/iso-evidence/README.md`](plugins/iso-evidence/README.md) for details.

## Setup (manual / development)

```bash
# 1. Install (editable for easy customizing)
pip install -e .
playwright install chromium

# 2. Notion access
#    - Create an internal integration: https://www.notion.so/my-integrations
#    - Copy the token into .env (see .env.example)
#    - Share the target Notion page with that integration
cp .env.example .env   # then edit NOTION_TOKEN

# 3. One-time GitHub login (opens a browser; log in, press Enter)
iso-evidence login
```

## Use it standalone (CLI)

```bash
iso-evidence screenshot "https://github.com/OWNER/REPO/actions/runs/123" -o run.png
iso-evidence screenshot "https://github.com/OWNER/REPO/pull/5" -s ".mergeability"
```

## Use it from Claude Code (MCP)

Add to your MCP config (`~/.claude.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "iso-evidence": {
      "command": "iso-evidence-mcp",
      "env": { "NOTION_TOKEN": "secret_xxx" }
    }
  }
}
```

Then ask the agent, e.g.:

> "Read the A.8.29 task from <notion-url>, then capture the Unit Tests Actions run and the PR checks, and attach them to that page with captions."

The agent will call `notion_get_task` → do/verify the work → `github_screenshot` (one per shot) → `notion_attach_evidence`.

## Customize

Small, single-purpose modules:

- `screenshot.py` — Playwright capture + login session (viewport, full-page, selectors, wait).
- `notion.py` — Notion read + File Upload API (swap for another tracker by reimplementing two methods).
- `server.py` — the three MCP tools.
- `cli.py` — `login` / `screenshot` commands.

## License

MIT.
