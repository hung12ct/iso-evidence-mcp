"""Minimal Notion client: read a task page, attach evidence images.

Uses the Notion File Upload API to upload local images and append them as
image blocks (with captions) to the target page.
"""

from __future__ import annotations

import re
from pathlib import Path

import httpx

API = "https://api.notion.com/v1"

# Notion block/property text lives under several keys; this covers the common ones.
_TEXTY_TYPES = (
    "paragraph",
    "heading_1",
    "heading_2",
    "heading_3",
    "bulleted_list_item",
    "numbered_list_item",
    "to_do",
    "quote",
    "callout",
    "toggle",
)


class Notion:
    def __init__(self, token: str, version: str = "2022-06-28") -> None:
        if not token:
            raise ValueError("NOTION_TOKEN is required")
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": version,
        }

    # --- helpers -------------------------------------------------------------

    # 32 hex chars, dashed (UUID) or undashed, as it appears in a Notion URL/id.
    _ID_RE = re.compile(
        r"[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?"
        r"[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}"
    )

    @classmethod
    def page_id(cls, url_or_id: str) -> str:
        """Extract a dashed UUID from a Notion URL or raw id.

        Notion URLs put the id last (after the title slug), so we take the last
        match to avoid hex letters in the slug corrupting it.
        """
        matches = cls._ID_RE.findall(url_or_id)
        if not matches:
            raise ValueError(f"Could not find a Notion page id in: {url_or_id!r}")
        h = re.sub(r"[^0-9a-fA-F]", "", matches[-1]).lower()
        return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

    @staticmethod
    def _rich_text(items: list[dict]) -> str:
        return "".join(part.get("plain_text", "") for part in items)

    # --- reads ---------------------------------------------------------------

    def get_task(self, url_or_id: str) -> dict:
        """Return ``{id, title, properties, text}`` for a page."""
        pid = self.page_id(url_or_id)
        with httpx.Client(headers=self._headers, timeout=30) as client:
            page = client.get(f"{API}/pages/{pid}").raise_for_status().json()
            blocks = (
                client.get(f"{API}/blocks/{pid}/children", params={"page_size": 100})
                .raise_for_status()
                .json()
            )

        title = ""
        properties: dict[str, str] = {}
        for name, prop in page.get("properties", {}).items():
            kind = prop.get("type")
            if kind == "title":
                title = self._rich_text(prop["title"])
                properties[name] = title
            elif kind == "rich_text":
                properties[name] = self._rich_text(prop["rich_text"])
            elif kind == "select":
                properties[name] = (prop.get("select") or {}).get("name", "")
            elif kind == "status":
                properties[name] = (prop.get("status") or {}).get("name", "")
            elif kind == "multi_select":
                properties[name] = ", ".join(
                    o["name"] for o in prop.get("multi_select", [])
                )

        lines: list[str] = []
        for block in blocks.get("results", []):
            kind = block.get("type")
            if kind in _TEXTY_TYPES:
                lines.append(self._rich_text(block[kind].get("rich_text", [])))

        return {
            "id": pid,
            "title": title,
            "properties": properties,
            "text": "\n".join(line for line in lines if line),
        }

    # --- writes --------------------------------------------------------------

    def attach_evidence(
        self,
        url_or_id: str,
        images: list[str],
        captions: list[str] | None = None,
    ) -> int:
        """Upload images and append them as captioned image blocks. Returns count."""
        pid = self.page_id(url_or_id)
        captions = captions or []
        children: list[dict] = []

        with httpx.Client(headers=self._headers, timeout=120) as client:
            for i, image in enumerate(images):
                path = Path(image)
                created = (
                    client.post(
                        f"{API}/file_uploads",
                        json={"filename": path.name, "content_type": "image/png"},
                    )
                    .raise_for_status()
                    .json()
                )
                with path.open("rb") as fh:
                    client.post(
                        created["upload_url"],
                        files={"file": (path.name, fh, "image/png")},
                    ).raise_for_status()

                caption = captions[i] if i < len(captions) else ""
                children.append(
                    {
                        "object": "block",
                        "type": "image",
                        "image": {
                            "type": "file_upload",
                            "file_upload": {"id": created["id"]},
                            "caption": (
                                [{"type": "text", "text": {"content": caption}}]
                                if caption
                                else []
                            ),
                        },
                    }
                )

            client.patch(
                f"{API}/blocks/{pid}/children", json={"children": children}
            ).raise_for_status()

        return len(children)
