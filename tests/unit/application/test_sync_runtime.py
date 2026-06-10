import pytest

from app.presentation.api.v1.sync_runtime import SyncExecutionRegistry


@pytest.mark.asyncio
async def test_sync_execution_registry_rejects_second_entry_until_exit():
    registry = SyncExecutionRegistry()

    first = await registry.try_enter('menu')
    second = await registry.try_enter('menu')
    await registry.exit('menu')
    third = await registry.try_enter('menu')

    assert first is True
    assert second is False
    assert third is True
