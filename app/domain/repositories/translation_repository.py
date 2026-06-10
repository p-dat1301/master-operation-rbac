from abc import ABC, abstractmethod

from app.domain.entities.translation import Translation


class TranslationRepository(ABC):
    @abstractmethod
    async def find_by_locale_key(self, locale: str, key: str) -> Translation | None:
        pass

    @abstractmethod
    async def find_all(self) -> list[Translation]:
        pass

    @abstractmethod
    async def create(self, translation: Translation) -> Translation:
        pass

    @abstractmethod
    async def update(self, translation: Translation) -> Translation:
        pass
