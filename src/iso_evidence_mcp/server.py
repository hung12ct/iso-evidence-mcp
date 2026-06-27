"""FastMCP server exposing the ISO-evidence tools.

Tools:
  - notion_get_task        read an ISO control / task page
  - github_screenshot      capture an (authenticated) GitHub page
  - notion_attach_evidence upload screenshots back onto the page
"""

from __future__ import annotations

import os
import tempfile

from fastmcp import FastMCP

from .notion import Notion
from .screenshot import capture

mcp = FastMCP("iso-evidence")


def _notion() -> Notion:
    return Notion(
        os.environ.get("NOTION_TOKEN", ""),
        os.environ.get("NOTION_VERSION", "2022-06-28"),
    )


@mcp.tool()
def notion_get_task(page: str) -> dict:
    """Read a Notion page (e.g. an ISO control/task).

    Args:
        page: Notion page URL or id.
    Returns:
        {id, title, properties, text} describing the task and what evidence it needs.
    """
    return _notion().get_task(page)


@mcp.tool()
async def github_screenshot(
    url: str, output_path: str = "", selector: str = ""
) -> str:
    """Screenshot a GitHub (or any) web page, reusing the saved login session.

    Args:
        url: Page to capture (e.g. an Actions run, a PR's checks, a file tree).
        output_path: Where to save the PNG. Defaults to a temp file.
        selector: Optional CSS selector to capture just one element.
    Returns:
        The path to the saved screenshot.
    """
    out = output_path or tempfile.mktemp(suffix=".png")
    saved = await capture(url, out, selector=selector or None)
    return str(saved)


@mcp.tool()
def notion_attach_evidence(
    page: str, images: list[str], captions: list[str] | None = None
) -> str:
    """Append local screenshot images to a Notion page as captioned image blocks.

    Args:
        page: Notion page URL or id.
        images: Local PNG paths (e.g. from github_screenshot).
        captions: Optional caption per image, same order.
    """
    count = _notion().attach_evidence(page, images, captions)
    return f"Attached {count} image(s) to the page."


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
