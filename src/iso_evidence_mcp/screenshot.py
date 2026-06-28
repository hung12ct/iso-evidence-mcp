"""Authenticated GitHub UI screenshots via Playwright.

A one-time interactive ``login`` saves the browser session (cookies) to disk;
subsequent captures reuse it headlessly so private GitHub pages render as if
you were logged in.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path

from playwright.async_api import Browser, Playwright, async_playwright


async def _launch_chromium(p: Playwright, *, headless: bool) -> Browser:
    """Launch Chromium, installing it on first use if the binary is missing."""
    try:
        return await p.chromium.launch(headless=headless)
    except Exception as exc:  # noqa: BLE001 - inspect message, then retry once
        message = str(exc)
        if "Executable doesn't exist" in message or "playwright install" in message:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
            )
            return await p.chromium.launch(headless=headless)
        raise

DEFAULT_SESSION = Path(
    os.environ.get(
        "ISO_EVIDENCE_SESSION",
        Path.home() / ".config" / "iso-evidence-mcp" / "session.json",
    )
)


async def save_login(
    session_path: Path = DEFAULT_SESSION,
    login_url: str = "https://github.com/login",
) -> Path:
    """Open a real browser, let the user log in, then persist the session."""
    session_path = Path(session_path)
    session_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await _launch_chromium(p, headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(login_url)
        print(
            "\n>> Log in to GitHub (incl. 2FA) in the opened browser.\n"
            ">> When you can see your logged-in homepage, press Enter here..."
        )
        await asyncio.get_event_loop().run_in_executor(None, input)
        await context.storage_state(path=str(session_path))
        await browser.close()

    print(f">> Session saved to {session_path}")
    return session_path


async def capture(
    url: str,
    output_path: str | Path,
    *,
    selector: str | None = None,
    session_path: Path = DEFAULT_SESSION,
    full_page: bool = True,
    wait_ms: int = 1500,
    width: int = 1440,
    height: int = 900,
) -> Path:
    """Screenshot ``url``. Reuses the saved session if present.

    If ``selector`` is given, only that element is captured; otherwise the full
    page is captured after a short settle delay.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    storage = str(session_path) if Path(session_path).exists() else None

    async with async_playwright() as p:
        browser = await _launch_chromium(p, headless=True)
        context = await browser.new_context(
            storage_state=storage,
            viewport={"width": width, "height": height},
        )
        page = await context.new_page()
        # GitHub and other SPAs keep connections open, so "networkidle" can
        # never fire — wait for the DOM to load, then settle for wait_ms.
        await page.goto(url, wait_until="load")
        if selector:
            element = await page.wait_for_selector(selector)
            await element.screenshot(path=str(output_path))
        else:
            await page.wait_for_timeout(wait_ms)
            await page.screenshot(path=str(output_path), full_page=full_page)
        await browser.close()

    return output_path
