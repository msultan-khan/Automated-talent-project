import re
from html import unescape


def normalize_text(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value or "")
    return cleaned.strip()


def strip_html(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html or "")
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return normalize_text(unescape(text))
