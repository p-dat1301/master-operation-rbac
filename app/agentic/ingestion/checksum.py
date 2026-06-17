"""Checksum helpers for ingestion metadata."""
from __future__ import annotations

from hashlib import sha256


def checksum_text(*parts: str) -> str:
    digest = sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"
