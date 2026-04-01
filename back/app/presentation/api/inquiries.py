from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.cs.create_inquiry import CreateInquiryCommand, CreateInquiryUseCase
from app.application.cs.list_inquiries import ListInquiriesUseCase
from app.core.dependencies import get_current_user_id
from app.infrastructure.persistence.cs_repo import SQLInquiryRepository
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.order_repo import SQLOrderRepository
from app.presentation.schemas.common import ApiResponse, PaginatedData

router = APIRouter(prefix="/inquiries", tags=["CS"])


class CreateInquiryRequest(BaseModel):
    order_id: int | None = None
    title: str
    content: str


@router.get("", response_model=ApiResponse[PaginatedData[dict]])
async def list_inquiries(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await ListInquiriesUseCase(SQLInquiryRepository(db)).execute(user_id, page, size)
    return ApiResponse(data=PaginatedData(
        items=[
            {
                "id": i.id,
                "title": i.title,
                "status": i.status,
                "answer": i.answer,
                "created_at": i.created_at,
            }
            for i in result.items
        ],
        total=result.total,
        page=page,
        size=size,
    ))


@router.post("", status_code=201)
async def create_inquiry(
    body: CreateInquiryRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    inquiry_id = await CreateInquiryUseCase(SQLInquiryRepository(db), SQLOrderRepository(db)).execute(
        CreateInquiryCommand(
            user_id=user_id,
            order_id=body.order_id,
            title=body.title,
            content=body.content,
        )
    )
    return ApiResponse(data={"id": inquiry_id, "message": "문의가 등록되었습니다."})
