from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.product.entities import Banner, Category, Product, ProductImage
from app.domain.product.repository import BannerRepository, CategoryRepository, ProductRepository
from app.infrastructure.persistence.models import BannerModel, CategoryModel, ProductImageModel, ProductModel


def _to_category(m: CategoryModel) -> Category:
    return Category(id=m.id, parent_id=m.parent_id, name=m.name, sort_order=m.sort_order, is_active=m.is_active)


def _to_product(m: ProductModel) -> Product:
    return Product(
        id=m.id,
        category_id=m.category_id,
        name=m.name,
        description=m.description,
        price=m.price,
        sale_price=m.sale_price,
        stock=m.stock,
        thumbnail_url=m.thumbnail_url,
        is_active=m.is_active,
        is_time_sale=m.is_time_sale,
        time_sale_start=m.time_sale_start,
        time_sale_end=m.time_sale_end,
        time_sale_price=m.time_sale_price,
        time_sale_stock=m.time_sale_stock,
        created_at=m.created_at,
        updated_at=m.updated_at,
        images=[ProductImage(id=i.id, product_id=i.product_id, url=i.url, sort_order=i.sort_order) for i in m.images],
    )


def _to_banner(m: BannerModel) -> Banner:
    return Banner(
        id=m.id, title=m.title, image_url=m.image_url, link_url=m.link_url,
        sort_order=m.sort_order, is_active=m.is_active,
        started_at=m.started_at, ended_at=m.ended_at, created_at=m.created_at,
    )


_SORT_MAP = {
    "latest": ProductModel.created_at.desc(),
    "price_asc": ProductModel.price.asc(),
    "price_desc": ProductModel.price.desc(),
}


class SQLCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def list_active(self) -> list[Category]:
        result = await self._s.execute(
            select(CategoryModel).where(CategoryModel.is_active == True).order_by(CategoryModel.sort_order)
        )
        return [_to_category(m) for m in result.scalars()]


class SQLProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def get_by_id(self, product_id: int) -> Product | None:
        result = await self._s.execute(
            select(ProductModel).options(selectinload(ProductModel.images)).where(ProductModel.id == product_id)
        )
        m = result.scalar_one_or_none()
        return _to_product(m) if m else None

    async def list(self, page: int, size: int, category_id: int | None, sort: str) -> tuple[list[Product], int]:
        q = select(ProductModel).options(selectinload(ProductModel.images)).where(ProductModel.is_active == True)
        if category_id:
            q = q.where(ProductModel.category_id == category_id)
        order = _SORT_MAP.get(sort, ProductModel.created_at.desc())
        q = q.order_by(order).offset((page - 1) * size).limit(size)

        count_q = select(func.count()).select_from(ProductModel).where(ProductModel.is_active == True)
        if category_id:
            count_q = count_q.where(ProductModel.category_id == category_id)

        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_product(m) for m in result.scalars()], total or 0

    async def search(self, query: str, page: int, size: int) -> tuple[list[Product], int]:
        pattern = f"%{query}%"
        q = (
            select(ProductModel)
            .options(selectinload(ProductModel.images))
            .where(ProductModel.is_active == True, ProductModel.name.like(pattern))
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = select(func.count()).select_from(ProductModel).where(
            ProductModel.is_active == True, ProductModel.name.like(pattern)
        )
        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_product(m) for m in result.scalars()], total or 0

    async def list_time_sale(self) -> list[Product]:
        now = datetime.now(timezone.utc)
        result = await self._s.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.images))
            .where(
                ProductModel.is_active == True,
                ProductModel.is_time_sale == True,
                ProductModel.time_sale_start <= now,
                ProductModel.time_sale_end >= now,
            )
            .order_by(ProductModel.time_sale_end.asc())
        )
        return [_to_product(m) for m in result.scalars()]

    async def save(self, product: Product) -> Product:
        m = ProductModel(
            category_id=product.category_id, name=product.name, description=product.description,
            price=product.price, sale_price=product.sale_price, stock=product.stock,
            thumbnail_url=product.thumbnail_url, is_active=product.is_active,
            is_time_sale=product.is_time_sale, time_sale_start=product.time_sale_start,
            time_sale_end=product.time_sale_end, time_sale_price=product.time_sale_price,
            time_sale_stock=product.time_sale_stock,
        )
        self._s.add(m)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_product(m)

    async def update(self, product: Product) -> Product:
        await self._s.execute(
            update(ProductModel).where(ProductModel.id == product.id).values(
                category_id=product.category_id, name=product.name, description=product.description,
                price=product.price, sale_price=product.sale_price, stock=product.stock,
                thumbnail_url=product.thumbnail_url, is_active=product.is_active,
                is_time_sale=product.is_time_sale, time_sale_start=product.time_sale_start,
                time_sale_end=product.time_sale_end, time_sale_price=product.time_sale_price,
                time_sale_stock=product.time_sale_stock,
            )
        )
        return product

    async def delete(self, product_id: int) -> None:
        m = await self._s.get(ProductModel, product_id)
        if m:
            m.is_active = False


class SQLBannerRepository(BannerRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def list_active(self) -> list[Banner]:
        now = datetime.now(timezone.utc)
        result = await self._s.execute(
            select(BannerModel).where(
                BannerModel.is_active == True,
                or_(BannerModel.started_at == None, BannerModel.started_at <= now),
                or_(BannerModel.ended_at == None, BannerModel.ended_at >= now),
            ).order_by(BannerModel.sort_order)
        )
        return [_to_banner(m) for m in result.scalars()]

    async def get_by_id(self, banner_id: int) -> Banner | None:
        m = await self._s.get(BannerModel, banner_id)
        return _to_banner(m) if m else None

    async def save(self, banner: Banner) -> Banner:
        m = BannerModel(
            title=banner.title, image_url=banner.image_url, link_url=banner.link_url,
            sort_order=banner.sort_order, is_active=banner.is_active,
            started_at=banner.started_at, ended_at=banner.ended_at,
        )
        self._s.add(m)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_banner(m)

    async def update(self, banner: Banner) -> Banner:
        await self._s.execute(
            update(BannerModel).where(BannerModel.id == banner.id).values(
                title=banner.title, image_url=banner.image_url, link_url=banner.link_url,
                sort_order=banner.sort_order, is_active=banner.is_active,
                started_at=banner.started_at, ended_at=banner.ended_at,
            )
        )
        return banner

    async def delete(self, banner_id: int) -> None:
        m = await self._s.get(BannerModel, banner_id)
        if m:
            await self._s.delete(m)
