import re
from typing import Any

import requests
from django.conf import settings

from utils.text_helpers import normalize_text, strip_html


class ExtractionError(Exception):
    pass


def _extract_meta_description(html: str) -> str:
    match = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        html,
        re.IGNORECASE,
    )
    if not match:
        return ""
    return normalize_text(match.group(1))


def _extract_title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return normalize_text(match.group(1))


def fetch_and_extract(url: str) -> dict[str, Any]:
    try:
        response = requests.get(
            url,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": "Zoho-Pipeline-MVP/1.0"},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ExtractionError(f"Failed to fetch URL: {url}") from exc

    html = response.text or ""
    if not html.strip():
        raise ExtractionError(f"Empty response body for URL: {url}")

    title = _extract_title(html)
    meta_description = _extract_meta_description(html)
    visible_text = strip_html(html)[:1000]

    if not any([title, meta_description, visible_text]):
        raise ExtractionError(f"No extractable content from URL: {url}")

    return {
        "url": url,
        "title": title or "Untitled",
        "snippet": meta_description or visible_text[:240],
        "text": visible_text,
    }
