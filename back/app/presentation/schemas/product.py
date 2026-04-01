from datetime import datetime, timezone

from pydantic import BaseModel


class ProductSummary(BaseModel):
    id: int
    name: str
    price: int
    sale_price: int | None
    thumbnail_url: str | None
    stock: int
    is_time_sale: bool
    time_sale_price: int | None
    time_sale_end: str | None


class ProductDetail(ProductSummary):
    category_id: int
    description: str | None
    images: list[dict]
    time_sale_start: str | None
    time_sale_stock: int | None
    created_at: str


class CategoryResponse(BaseModel):
    id: int
    parent_id: int | None
    name: str
    sort_order: int


class BannerResponse(BaseModel):
    id: int
    title: str
    image_url: str
    link_url: str | None
    sort_order: int
