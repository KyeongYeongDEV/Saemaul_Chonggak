from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.infrastructure.cache.redis_client import close_redis, get_redis
from app.presentation.api import auth, banners, cart, categories, coupons, faqs, inquiries, notices, orders, payments, products, reviews, users
from app.presentation.admin import banners as admin_banners
from app.presentation.admin import coupons as admin_coupons
from app.presentation.admin import dashboard, orders as admin_orders
from app.presentation.admin import products as admin_products
from app.presentation.admin import stats
from app.presentation.admin import users as admin_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_redis()
    yield
    await close_redis()


app = FastAPI(
    title="새마을총각 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
)

# CORS
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 공통 에러 핸들러
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )


# API 라우터 등록
PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(products.router, prefix=PREFIX)
app.include_router(categories.router, prefix=PREFIX)
app.include_router(banners.router, prefix=PREFIX)
app.include_router(cart.router, prefix=PREFIX)
app.include_router(coupons.router, prefix=PREFIX)
app.include_router(payments.router, prefix=PREFIX)
app.include_router(orders.router, prefix=PREFIX)
app.include_router(reviews.router, prefix=PREFIX)
app.include_router(faqs.router, prefix=PREFIX)
app.include_router(notices.router, prefix=PREFIX)
app.include_router(inquiries.router, prefix=PREFIX)

# Admin 라우터
app.include_router(dashboard.router, prefix=PREFIX)
app.include_router(admin_orders.router, prefix=PREFIX)
app.include_router(admin_products.router, prefix=PREFIX)
app.include_router(admin_users.router, prefix=PREFIX)
app.include_router(admin_banners.router, prefix=PREFIX)
app.include_router(admin_coupons.router, prefix=PREFIX)
app.include_router(stats.router, prefix=PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}
