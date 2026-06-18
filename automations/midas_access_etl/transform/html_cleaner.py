from __future__ import annotations

import html
import re

HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
INVALID_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean_text(value: str | None) -> str:
    if value is None:
        return ""
    text = html.unescape(value)
    text = HTML_TAG_RE.sub(" ", text)
    text = INVALID_CHAR_RE.sub(" ", text)
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text
