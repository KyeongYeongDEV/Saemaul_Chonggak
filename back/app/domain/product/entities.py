from dataclasses import dataclass, field
from datetime import datetime

from app.domain.product.exceptions import OutOfStockException


@dataclass
class Category:
    id: int | None
    parent_id: int | None
    name: str
    sort_order: int
    is_active: bool


@dataclass
class ProductImage:
    id: int | None
    product_id: int
    url: str
    sort_order: int


@dataclass
class Banner:
    id: int | None
    title: str
    image_url: str
    link_url: str | None
    sort_order: int
    is_active: bool
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime


@dataclass
class Product:
    id: int | None
    category_id: int
    name: str
    description: str | None
    price: int
    sale_price: int | None
    stock: int
    thumbnail_url: str | None
    is_active: bool
    is_time_sale: bool
    time_sale_start: datetime | None
    time_sale_end: datetime | None
    time_sale_price: int | None
    time_sale_stock: int | None
    created_at: datetime
    updated_at: datetime | None = None
    images: list[ProductImage] = field(default_factory=list)

    def effective_price(self) -> int:
        """타임세일 > 할인가 > 원가 순."""
        now = datetime.utcnow()
        if (
            self.is_time_sale
            and self.time_sale_price is not None
            and self.time_sale_start
            and self.time_sale_end
            and self.time_sale_start <= now <= self.time_sale_end
        ):
            return self.time_sale_price
        if self.sale_price is not None:
            return self.sale_price
        return self.price

    def decrease_stock(self, quantity: int) -> None:
        if self.stock < quantity:
            raise OutOfStockException()
        self.stock -= quantity
