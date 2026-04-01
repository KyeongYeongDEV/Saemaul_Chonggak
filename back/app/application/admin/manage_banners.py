from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.domain.product.entities import Banner
from app.domain.product.repository import BannerRepository
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository


@dataclass
class BannerCommand:
    title: str
    image_url: str
    link_url: str | None
    sort_order: int
    is_active: bool
    started_at: datetime | None
    ended_at: datetime | None
    admin_id: int
    ip_address: str | None


class AdminBannerUseCase:
    def __init__(
        self, banner_repo: BannerRepository, audit_repo: AuditLogRepository, cache: CacheService
    ):
        self._repo = banner_repo
        self._audit = audit_repo
        self._cache = cache

    async def list(self) -> list[Banner]:
        return await self._repo.list_active()

    async def create(self, cmd: BannerCommand) -> Banner:
        banner = Banner(
            id=None, title=cmd.title, image_url=cmd.image_url, link_url=cmd.link_url,
            sort_order=cmd.sort_order, is_active=cmd.is_active,
            started_at=cmd.started_at, ended_at=cmd.ended_at, created_at=datetime.now(timezone.utc),
        )
        saved = await self._repo.save(banner)
        await self._audit.write(
            admin_id=cmd.admin_id, action="CREATE_BANNER",
            target_type="banner", target_id=saved.id, ip_address=cmd.ip_address,
        )
        await self._cache.invalidate("banner:list")
        return saved

    async def update(self, banner_id: int, cmd: BannerCommand) -> Banner:
        banner = Banner(
            id=banner_id, title=cmd.title, image_url=cmd.image_url, link_url=cmd.link_url,
            sort_order=cmd.sort_order, is_active=cmd.is_active,
            started_at=cmd.started_at, ended_at=cmd.ended_at, created_at=datetime.now(timezone.utc),
        )
        updated = await self._repo.update(banner)
        await self._cache.invalidate("banner:list")
        return updated

    async def delete(self, banner_id: int, admin_id: int, ip_address: str | None) -> None:
        await self._repo.delete(banner_id)
        await self._cache.invalidate("banner:list")
