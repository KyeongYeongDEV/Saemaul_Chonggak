from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.product.entities import Banner, Category, Product


class CategoryRepository(ABC):
    @abstractmethod
    async def list_active(self) -> list[Category]: ...


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product | None: ...

    @abstractmethod
    async def list(
        self,
        page: int,
        size: int,
        category_id: int | None,
        sort: str,
    ) -> tuple[list[Product], int]: ...

    @abstractmethod
    async def search(
        self, query: str, page: int, size: int
    ) -> tuple[list[Product], int]: ...

    @abstractmethod
    async def list_time_sale(self) -> list[Product]: ...

    @abstractmethod
    async def save(self, product: Product) -> Product: ...

    @abstractmethod
    async def update(self, product: Product) -> Product: ...

    @abstractmethod
    async def delete(self, product_id: int) -> None: ...


class BannerRepository(ABC):
    @abstractmethod
    async def list_active(self) -> list[Banner]: ...

    @abstractmethod
    async def save(self, banner: Banner) -> Banner: ...

    @abstractmethod
    async def update(self, banner: Banner) -> Banner: ...

    @abstractmethod
    async def delete(self, banner_id: int) -> None: ...

    @abstractmethod
    async def get_by_id(self, banner_id: int) -> Banner | None: ...
