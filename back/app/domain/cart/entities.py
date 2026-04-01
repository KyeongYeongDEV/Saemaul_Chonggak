from dataclasses import dataclass, field


@dataclass
class CartItem:
    product_id: int
    quantity: int


@dataclass
class Cart:
    user_id: int
    items: list[CartItem] = field(default_factory=list)

    def add_item(self, product_id: int, quantity: int) -> None:
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product_id=product_id, quantity=quantity))

    def update_item(self, product_id: int, quantity: int) -> None:
        for item in self.items:
            if item.product_id == product_id:
                item.quantity = quantity
                return

    def remove_item(self, product_id: int) -> None:
        self.items = [i for i in self.items if i.product_id != product_id]

    def clear(self) -> None:
        self.items = []

    @property
    def item_count(self) -> int:
        return sum(i.quantity for i in self.items)
