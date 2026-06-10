from __future__ import annotations

import json
import os
from pathlib import Path


class AdminConfigSeedLoader:
    def __init__(self, seed_dir: str | Path | None = None) -> None:
        base_dir = Path(seed_dir or os.environ.get("SYNC_SEED_DIR") or "app/infrastructure/database/seed_assets/admin_config")
        self._seed_dir = base_dir

    def _read_json(self, filename: str):
        path = self._seed_dir / filename
        return json.loads(path.read_text(encoding="utf-8"))

    async def load_menu(self):
        return self._read_json("menu.json")

    async def load_i18n(self):
        return {
            "vi": self._read_json("vi.json"),
            "en": self._read_json("en.json"),
        }
