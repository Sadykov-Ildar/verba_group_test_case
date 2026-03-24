import json

from dtos import Product, ProductCard


class WildberriesAPIParser:
    @staticmethod
    def parse_product(product: dict):
        product_id = product.get("id", 0)
        link = ""
        if product_id:
            link = f"https://www.wildberries.ru/catalog/{product['id']}/detail.aspx"

        price = 0
        sizes = product.get("sizes", [])
        sizes_str = ""
        if sizes:
            try:
                # Цена приходит в копейках, превращаем в рубли
                price = sizes[0]["price"]["basic"] / 100
            except KeyError:
                price = 0
            sizes_str = ", ".join(x["name"] for x in sizes)

        supplier_link = ""
        supplier_id = product.get("supplierId", "")
        if supplier_id:
            supplier_link = f"https://www.wildberries.ru/seller/{supplier_id}"

        parsed_product = Product(
            link=link,
            product_id=product_id,
            name=product.get("name", ""),
            price=price,
            description="",
            images="",
            options="",
            supplier=product.get("supplier", ""),
            supplier_link=supplier_link,
            sizes=sizes_str,
            quantity=product.get("totalQuantity", 0),
            reviewRating=product.get("reviewRating", 0),
            feedbacks_count=product.get("feedbacks", 0),
        )
        return parsed_product

    @staticmethod
    def parse_card(card: dict, product: Product) -> ProductCard:
        options = card.get("options", [])
        options = {x["name"]: x["value"] for x in options}

        return ProductCard(
            description=card.get("description", ""),
            images=_get_images_str(
                product, card.get("media", {}).get("photo_count", 0)
            ),
            options=json.dumps(options, ensure_ascii=False),
        )


def _get_images_str(product: Product, photo_count: int):
    return ", ".join(
        f"https://basket-{product.basket_num}.wbbasket.ru/vol{product.vol}/part{product.part}/{product.product_id}/images/big/{i + 1}.webp"
        for i in range(photo_count)
    )
