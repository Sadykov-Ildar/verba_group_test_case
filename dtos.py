from dataclasses import dataclass, astuple

from basket import get_basket_num


@dataclass
class Product:
    link: str
    product_id: int
    name: str
    price: int  # в рублях
    description: str
    images: str
    options: str
    supplier: str
    supplier_link: str
    sizes: str
    quantity: int
    reviewRating: int
    feedbacks_count: int

    @property
    def vol(self):
        return self.product_id // 100000

    @property
    def part(self):
        return self.product_id // 1000

    @property
    def basket_num(self):
        return get_basket_num(self.vol)

    def as_xlsx_row(self) -> tuple:
        return astuple(self)


@dataclass
class ProductCard:
    description: str
    images: str
    options: str


@dataclass()
class PriceRange:
    total: int
    min_price: int
    max_price: int
