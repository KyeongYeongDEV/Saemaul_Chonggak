from __future__ import annotations

from dataclasses import dataclass

from app.core.exceptions import UserNotFoundError
from app.domain.user.repository import UserRepository
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository


@dataclass
class UserListResult:
    items: list[dict]
    total: int


class AdminUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        audit_repo: AuditLogRepository,
    ):
        self._user_repo = user_repo
        self._audit = audit_repo

    async def list(self, page: int, size: int) -> UserListResult:
        users, total = await self._user_repo.list_paginated(page, size)
        items = [
            {"id": u.id, "email": u.email, "name": u.name, "is_active": u.is_active, "role": u.role.value}
            for u in users
        ]
        return UserListResult(items=items, total=total)

    async def suspend(self, user_id: int, admin_id: int, ip_address: str | None) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        user.is_active = False
        await self._user_repo.update(user)
        await self._audit.write(
            admin_id=admin_id, action="SUSPEND_USER",
            target_type="user", target_id=user_id, ip_address=ip_address,
        )
