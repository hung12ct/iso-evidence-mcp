# iso-evidence (Claude Code plugin)

Bundles the [`iso-evidence-mcp`](../../README.md) server so Claude Code can:

1. read a task/control from **Notion**,
2. capture **authenticated GitHub** screenshots (Actions runs, PR checks, file trees),
3. upload them back onto the Notion page as captioned evidence.

## Install

```
/plugin marketplace add hung12ct/iso-evidence-mcp
/plugin install iso-evidence@iso-evidence-official
```

Then run `/mcp` to confirm the **iso-evidence** server is connected.

## One-time setup

The plugin runs the server via `uvx` straight from GitHub, so you need:

1. **uv** installed — `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **`NOTION_TOKEN`** exported in your shell (see the root README for how to create the Notion integration and share the page):
   ```bash
   export NOTION_TOKEN=ntn_xxx   # add to ~/.zshrc to persist
   ```
3. **GitHub login** captured once (saves a browser session for screenshots):
   ```bash
   uvx --from git+https://github.com/hung12ct/iso-evidence-mcp.git iso-evidence login
   ```
   Chromium is downloaded automatically on first use.

## Tools

| Tool | Purpose |
|---|---|
| `notion_get_task(page)` | Read an ISO control / task page. |
| `github_screenshot(url, output_path?, selector?)` | Screenshot an authenticated GitHub page. |
| `notion_attach_evidence(page, images, captions?)` | Upload screenshots back to the page. |
