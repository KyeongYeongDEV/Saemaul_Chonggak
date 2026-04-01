from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models import AuditLogModel


class AuditLogRepository:
    def __init__(self, session: AsyncSession):
        self._s = session

    async def write(
        self,
        admin_id: int,
        action: str,
        target_type: str,
        target_id: int | None = None,
        before_data: dict | None = None,
        after_data: dict | None = None,
        ip_address: str | None = None,
    ) -> None:
        m = AuditLogModel(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address,
        )
        self._s.add(m)
        await self._s.flush()
