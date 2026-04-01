from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.admin.manage_users import AdminUserUseCase
from app.core.dependencies import require_admin
from app.infrastructure.persistence.audit_log_repo import AuditLogRepository
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.user_repo import SQLUserRepository
from app.presentation.schemas.common import ApiResponse, PaginatedData

router = APIRouter(prefix="/admin/users", tags=["Admin"])


@router.get("", response_model=ApiResponse[PaginatedData[dict]])
async def list_users(
    page: int = Query(1, ge=1), size: int = Query(20),
    admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db),
):
    use_case = AdminUserUseCase(SQLUserRepository(db), AuditLogRepository(db), db)
    result = await use_case.list(page, size)
    return ApiResponse(data=PaginatedData(items=result.items, total=result.total, page=page, size=size))


@router.patch("/{user_id}/suspend", status_code=204)
async def suspend_user(
    user_id: int, request: Request,
    admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db),
):
    use_case = AdminUserUseCase(SQLUserRepository(db), AuditLogRepository(db), db)
    await use_case.suspend(user_id, int(admin["sub"]), request.client.host if request.client else None)
