"""CLI: one-time GitHub login + manual screenshot capture."""

from __future__ import annotations

import asyncio

import click

from .screenshot import capture, save_login


@click.group()
def cli() -> None:
    """iso-evidence: capture authenticated GitHub screenshots for audit evidence."""


@cli.command()
def login() -> None:
    """Open a browser to log in to GitHub once and save the session."""
    asyncio.run(save_login())


@cli.command()
@click.argument("url")
@click.option("-o", "--output", default="screenshot.png", help="Output PNG path.")
@click.option("-s", "--selector", default=None, help="CSS selector to capture.")
def screenshot(url: str, output: str, selector: str | None) -> None:
    """Capture a screenshot of URL using the saved session."""
    path = asyncio.run(capture(url, output, selector=selector))
    click.echo(str(path))


if __name__ == "__main__":
    cli()
