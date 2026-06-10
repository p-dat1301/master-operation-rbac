from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.translation import Translation
from app.domain.repositories.translation_repository import TranslationRepository
from app.infrastructure.database.models.translation_model import TranslationModel


class SQLAlchemyTranslationRepository(TranslationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: TranslationModel) -> Translation:
        return Translation(
            id=model.id,
            locale=model.locale,
            key=model.key,
            value=model.value,
            namespace=model.namespace,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def find_by_locale_key(self, locale: str, key: str) -> Translation | None:
        stmt = select(TranslationModel).where(TranslationModel.locale == locale, TranslationModel.key == key)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_all(self) -> list[Translation]:
        stmt = select(TranslationModel).order_by(TranslationModel.locale, TranslationModel.key)
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, translation: Translation) -> Translation:
        model = TranslationModel(
            locale=translation.locale,
            key=translation.key,
            value=translation.value,
            namespace=translation.namespace,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, translation: Translation) -> Translation:
        stmt = select(TranslationModel).where(TranslationModel.id == translation.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model is None:
            raise ValueError(f"Translation {translation.id} not found")
        model.locale = translation.locale
        model.key = translation.key
        model.value = translation.value
        model.namespace = translation.namespace
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
