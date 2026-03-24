import json
import os

from dtos import Product
from get_token import get_token
from wb_api import WildberriesAPIHandler
from to_xlsx import save_to_xlsx
from wb_network import WildberriesDataFetcher
from wb_parser import WildberriesAPIParser


def get_filtered_products(
    products: list[Product], min_rating: int | float, max_price: int, country: str
):
    """
    Отфильтровываем найденные товары
    :param products: весь список товаров
    :param min_rating: Минимально допустимый рейтинг
    :param max_price: Максимально допустимая цена
    :param country: Страна производства
    :return:
    """
    country = country.lower()
    result = []
    for product in products:
        if product.reviewRating < min_rating:
            continue
        if product.price > max_price:
            continue
        if product.options:
            parsed_options = json.loads(product.options)
            product_country = parsed_options.get("Страна производства", "")
            if product_country.lower() != country:
                continue

        result.append(product)

    return result


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    cookies = {
        "x_wbaas_token": get_token(),
    }
    search_str = "пальто из натуральной шерсти"

    api = WildberriesAPIHandler(
        parser=WildberriesAPIParser(),
        wb_repo=WildberriesDataFetcher(search_str=search_str, cookies=cookies),
    )
    products = api.get_products()
    save_to_xlsx(products, "results/products.xlsx")

    filtered_products = get_filtered_products(products, 4.5, 10000, "Россия")
    save_to_xlsx(filtered_products, "results/filtered_products.xlsx")


if __name__ == "__main__":
    main()
