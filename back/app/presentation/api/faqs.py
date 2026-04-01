from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.cs.list_faqs import ListFaqsUseCase
from app.infrastructure.persistence.cs_repo import SQLFaqRepository
from app.infrastructure.persistence.database import get_db
from app.presentation.schemas.common import ApiResponse

router = APIRouter(prefix="/faqs", tags=["CS"])


@router.get("", response_model=ApiResponse[list[dict]])
async def list_faqs(db: AsyncSession = Depends(get_db)):
    faqs = await ListFaqsUseCase(SQLFaqRepository(db)).execute()
    return ApiResponse(data=[
        {"id": f.id, "category": f.category, "question": f.question, "answer": f.answer}
        for f in faqs
    ])
