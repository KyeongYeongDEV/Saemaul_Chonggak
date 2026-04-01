from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserNotFoundError
from app.domain.user.repository import UserRepository
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository
from app.infrastructure.persistence.models import UserModel


@dataclass
class UserListResult:
    items: list[dict]
    total: int


class AdminUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        audit_repo: AuditLogRepository,
        session: AsyncSession,
    ):
        self._user_repo = user_repo
        self._audit = audit_repo
        self._session = session

    async def list(self, page: int, size: int) -> UserListResult:
        q = (
            select(UserModel)
            .order_by(UserModel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = select(func.count()).select_from(UserModel)
        result = await self._session.execute(q)
        total = await self._session.scalar(count_q)
        items = [
            {"id": m.id, "email": m.email, "name": m.name, "is_active": m.is_active, "role": m.role}
            for m in result.scalars()
        ]
        return UserListResult(items=items, total=total or 0)

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
