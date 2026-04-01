from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.review.create_review import CreateReviewCommand, CreateReviewUseCase
from app.application.review.list_reviews import ListReviewsUseCase
from app.core.dependencies import get_current_user_id
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.order_repo import SQLOrderRepository
from app.infrastructure.persistence.review_repo import SQLReviewRepository
from app.presentation.schemas.common import ApiResponse, PaginatedData
from pydantic import BaseModel

router = APIRouter(prefix="/reviews", tags=["Reviews"])


class CreateReviewRequest(BaseModel):
    order_id: int
    product_id: int
    rating: int
    content: str | None = None


@router.get("/{product_id}", response_model=ApiResponse[PaginatedData[dict]])
async def list_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await ListReviewsUseCase(SQLReviewRepository(db)).execute(product_id, page, size)
    items = [{"id": r.id, "rating": r.rating, "content": r.content, "created_at": str(r.created_at)} for r in result.items]
    return ApiResponse(data=PaginatedData(items=items, total=result.total, page=page, size=size))


@router.post("", status_code=201)
async def create_review(
    body: CreateReviewRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await CreateReviewUseCase(SQLOrderRepository(db), SQLReviewRepository(db)).execute(
        CreateReviewCommand(user_id=user_id, order_id=body.order_id, product_id=body.product_id,
                            rating=body.rating, content=body.content)
    )
    return ApiResponse(data={"message": "리뷰가 등록되었습니다."})
