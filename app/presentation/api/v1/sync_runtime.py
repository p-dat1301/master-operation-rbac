from __future__ import annotations

import asyncio
import os


class SyncExecutionRegistry:
    def __init__(self) -> None:
        self._guard = asyncio.Lock()
        self._in_progress: set[str] = set()

    async def try_enter(self, resource: str) -> bool:
        async with self._guard:
            if resource in self._in_progress:
                return False
            self._in_progress.add(resource)
            return True

    async def exit(self, resource: str) -> None:
        async with self._guard:
            self._in_progress.discard(resource)


async def maybe_delay_for_sync_test() -> None:
    delay_ms = int(os.environ.get('SYNC_TEST_DELAY_MS', '0') or '0')
    if delay_ms > 0:
        await asyncio.sleep(delay_ms / 1000)


sync_execution_registry = SyncExecutionRegistry()
