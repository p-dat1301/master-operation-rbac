"""Checksum helpers for ingestion stage."""
from __future__ import annotations

import hashlib


def checksum_text(*parts: str) -> str:
    hasher = hashlib.sha256()
    for part in parts:
        hasher.update(part.encode("utf-8"))
        hasher.update(b"\0")
    return f"sha256:{hasher.hexdigest()}"
