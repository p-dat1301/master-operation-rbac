from __future__ import annotations

from app.application.dtos.i18n_sync import I18nSyncSummary
from app.domain.entities.translation import Translation
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation
from app.domain.repositories.translation_repository import TranslationRepository
from app.domain.services.rbac_service import RBACService


class I18nSyncValidationError(BusinessRuleViolation):
    def __init__(self, summary: I18nSyncSummary) -> None:
        super().__init__("i18n sync validation failed")
        self.summary = summary


class I18nSyncUseCase:
    def __init__(
        self,
        translation_repo: TranslationRepository,
        seed_loader,
        rbac_service: RBACService,
    ) -> None:
        self.translation_repo = translation_repo
        self.seed_loader = seed_loader
        self.rbac_service = rbac_service

    async def execute(self, actor: User, dry_run: bool = False) -> I18nSyncSummary:
        self.rbac_service.require_permission(actor, "system.config.manage")
        try:
            raw_by_locale = await self.seed_loader.load_i18n()
        except (OSError, TypeError, ValueError) as exc:
            summary = I18nSyncSummary(resource="i18n", created=0, updated=0, skipped=0, errors=[f"i18n seed invalid: {exc}"], dry_run=dry_run)
            raise I18nSyncValidationError(summary) from exc
        summary = await self._sync(raw_by_locale, dry_run=dry_run)
        if summary.errors:
            raise I18nSyncValidationError(summary)
        return summary

    async def _sync(self, raw_by_locale, dry_run: bool) -> I18nSyncSummary:
        errors: list[str] = []
        if not isinstance(raw_by_locale, dict):
            return I18nSyncSummary(resource="i18n", created=0, updated=0, skipped=0, errors=["i18n seed must be an object keyed by locale"], dry_run=dry_run)

        normalized_items: list[dict] = []
        seen_locale_keys: set[tuple[str, str]] = set()
        keys_by_locale: dict[str, set[str]] = {}

        for locale, raw_items in raw_by_locale.items():
            if not isinstance(locale, str) or not locale.strip():
                errors.append("locale key must be a non-empty string")
                continue
            if not isinstance(raw_items, list):
                errors.append(f"{locale}.json must be an array")
                continue

            locale_keys: set[str] = set()
            for index, item in enumerate(raw_items):
                if not isinstance(item, dict):
                    errors.append(f"{locale}.json item[{index}] must be an object")
                    continue
                missing = [field for field in ["locale", "key", "value", "namespace"] if field not in item]
                if missing:
                    errors.append(f"{locale}.json item[{index}] missing required fields: {', '.join(missing)}")
                    continue
                item_locale = item["locale"]
                if item_locale != locale:
                    errors.append(f"{locale}.json item[{index}] locale must be {locale}")
                    continue
                key = item["key"]
                if not isinstance(key, str) or not key.strip():
                    errors.append(f"{locale}.json item[{index}] key must be a non-empty string")
                    continue
                if (locale, key) in seen_locale_keys:
                    errors.append(f"duplicate locale key: {locale}.{key}")
                    continue
                value = item["value"]
                if not isinstance(value, str):
                    errors.append(f"{locale}.json item[{index}] value must be a string")
                    continue
                namespace = item["namespace"]
                if not isinstance(namespace, str) or not namespace.strip():
                    errors.append(f"{locale}.json item[{index}] namespace must be a non-empty string")
                    continue
                normalized = {
                    "locale": locale,
                    "key": key,
                    "value": value,
                    "namespace": namespace,
                }
                normalized_items.append(normalized)
                seen_locale_keys.add((locale, key))
                locale_keys.add(key)
            keys_by_locale[locale] = locale_keys

        if errors:
            return I18nSyncSummary(resource="i18n", created=0, updated=0, skipped=0, errors=errors, dry_run=dry_run)

        expected_keys = set().union(*keys_by_locale.values()) if keys_by_locale else set()
        for locale, locale_keys in sorted(keys_by_locale.items()):
            for missing_key in sorted(expected_keys - locale_keys):
                errors.append(f"missing locale key: {locale}.{missing_key}")

        existing_translations = await self.translation_repo.find_all()
        existing_by_locale_key = {(translation.locale, translation.key): translation for translation in existing_translations}

        if errors:
            return I18nSyncSummary(resource="i18n", created=0, updated=0, skipped=0, errors=errors, dry_run=dry_run)

        created = 0
        updated = 0
        skipped = 0

        for item in sorted(normalized_items, key=lambda row: (row["locale"], row["key"])):
            current = existing_by_locale_key.get((item["locale"], item["key"]))
            payload = Translation(
                id=current.id if current else 0,
                locale=item["locale"],
                key=item["key"],
                value=item["value"],
                namespace=item["namespace"],
                created_at=current.created_at if current else None,
                updated_at=current.updated_at if current else None,
            )
            if current is None:
                created += 1
                if not dry_run:
                    await self.translation_repo.create(payload)
                continue
            if self._same_translation(current, payload):
                skipped += 1
                continue
            updated += 1
            if not dry_run:
                await self.translation_repo.update(payload)

        seed_locale_keys = {(item["locale"], item["key"]) for item in normalized_items}
        for locale_key in existing_by_locale_key:
            if locale_key not in seed_locale_keys:
                skipped += 1

        return I18nSyncSummary(resource="i18n", created=created, updated=updated, skipped=skipped, errors=[], dry_run=dry_run)

    def _same_translation(self, current: Translation, payload: Translation) -> bool:
        return (
            current.locale == payload.locale
            and current.key == payload.key
            and current.value == payload.value
            and current.namespace == payload.namespace
        )
