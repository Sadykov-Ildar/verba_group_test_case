import random
import time

from dtos import Product, PriceRange


class WildberriesAPIHandler:
    """
    Основной класс для работы с WB
    """

    def __init__(self, wb_repo, parser):
        # Класс для работы с сетью
        self.wb_repo = wb_repo
        # Парсер json-ответов
        self.parser = parser

        # Оставляем только товары с уникальными артикулами
        self.__seen_product_ids = set()

    def get_wb_prices(self, min_price=0, max_price=0):
        """
        Получаем количество товаров, отфильтрованных по цене
        Если ценовой фильтр не указан, то извлекаем минимальную и максимальную цену из ответа
        """
        data = self.wb_repo.get_prices(min_price=min_price, max_price=max_price)

        total = data.get("data", {}).get("total", 0)

        filters = data.get("data", {}).get("filters", [])

        if not min_price or not max_price:
            for item in filters:
                if item.get("name") == "Цена":
                    min_price = item.get("minPriceU")
                    max_price = item.get("maxPriceU")
                    break

        if not all([total, min_price, max_price]):
            return None

        return PriceRange(
            total=total,
            min_price=min_price,
            max_price=max_price,
        )

    def get_products(self) -> list[Product]:
        """
        Получаем список товаров

        WB отказывается отдавать уникальные артикулы при пагинации запросов где-то с 3 страницы.
        Чтобы собрать все уникальные товары, мы делим ценовой диапазон до тех пор,
        пока в ответе не получим менее 100 товаров - тогда их можно получить одним запросом,
        не заморачиваясь с пагинацией.
        """
        price_range = self.get_wb_prices()
        if not price_range:
            return []

        products: list[Product] = []
        stack = [price_range]
        while stack:
            price_range = stack.pop()
            print(price_range)
            if price_range.total >= 100:
                min_rub = price_range.min_price // 100
                max_rub = price_range.max_price // 100

                if min_rub >= max_rub:
                    continue

                mid_rub = (min_rub + max_rub) // 2
                mid = mid_rub * 100

                price_range_left = self.get_wb_prices(price_range.min_price, mid)
                price_range_right = self.get_wb_prices(mid + 100, price_range.max_price)

                if price_range_left:
                    stack.append(price_range_left)
                if price_range_right:
                    stack.append(price_range_right)
            else:
                products.extend(
                    self._get_wb_catalog_by_price(
                        price_range.min_price, price_range.max_price
                    )
                )

        self.update_products_with_options(products)

        return products

    def update_products_with_options(self, products: list[Product]):
        """
        WB отдает не все данные, так что нам нужно дополнительно запросить карточки товаров,
        чтобы собрать описание, характеристики и ссылки на изображения.
        """
        report_batches = 100
        total_products = len(products)
        for index, product in enumerate(products, start=1):
            if index % report_batches == 0:
                print(f"processed {index} out of {total_products} products...")
                sleep_normal()
            self._update_product_from_card(product)

    def _get_wb_catalog_by_price(self, min_price, max_price) -> list[Product]:
        """
        Запрашиваем каталог товаром и парсим ответ.
        """
        data = self.wb_repo.get_catalog(min_price, max_price)
        products = []
        for product_dict in data.get("products", []):
            product = self.parser.parse_product(product_dict)
            product_id = product.product_id
            if product_id not in self.__seen_product_ids:
                products.append(product)
                self.__seen_product_ids.add(product_id)

        return products

    def _update_product_from_card(self, product: Product):
        """
        Дополняем данные товара из его карточки
        """
        card = self.wb_repo.get_card(product)
        parsed_card = self.parser.parse_card(card, product)

        product.description = parsed_card.description
        product.options = parsed_card.options
        product.images = parsed_card.images


def sleep_normal(seconds=2.0, sigma=1.0):
    time_to_sleep = random.normalvariate(seconds, sigma)
    if time_to_sleep < 0:
        time_to_sleep = -time_to_sleep
    time.sleep(time_to_sleep)
