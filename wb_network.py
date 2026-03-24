from urllib.parse import quote

import requests

from dtos import Product

SEARCH_URL = (
    "https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search"
)


class WildberriesDataFetcher:
    """
    Класс для получения данных из WB по сети.
    Не стал заменять requests на aiohttp для простоты и чтобы не спамить WB
    """

    def __init__(self, search_str, cookies):
        self.search_str = search_str
        self.cookies = cookies

    def get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": f"https://www.wildberries.ru/catalog/0/search.aspx?search={quote(self.search_str, safe='/', encoding=None, errors=None)}",
            "x-requested-with": "XMLHttpRequest",
            "x-spa-version": "14.2.4",
            "x-userid": "0",
            "Sec-GPC": "1",
            # "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=4",
        }

    def get_search_params(self, min_price: int = 0, max_price: int = 0):
        params = {
            "ab_testing": "false",
            "appType": "1",
            "curr": "rub",
            "dest": "-3314466",
            "hide_vflags": "4294967296",
            "inheritFilters": "false",
            "lang": "ru",
            "query": self.search_str,
            "sort": "popular",
            "spp": "100",
            "suppressSpellcheck": "false",
        }
        if min_price and max_price:
            params.update({"priceU": f"{min_price};{max_price}"})

        return params

    def fetch_data(self, params: dict, add_headers: dict = None, url=None):
        headers = self.get_headers()
        if add_headers:
            headers.update(add_headers)
        if url is None:
            url = SEARCH_URL

        # Тут надо бы добавить retry, обработку ошибок и логирование...
        response = requests.get(
            url,
            params=params,
            headers=headers,
            cookies=self.cookies,
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Error: request for {url} ended with {response.status_code} status code"
            )

        return {}

    def get_prices(self, min_price: int = 0, max_price: int = 0):
        """
        Запрос за фильтрами каталога
        """
        params = self.get_search_params(min_price, max_price)

        params.update(
            {
                "resultset": "filters",
            }
        )

        return self.fetch_data(params=params)

    def get_catalog(self, min_price, max_price):
        """
        Запрос за товарами из каталога
        """
        params = self.get_search_params(min_price, max_price)

        params.update(
            {
                "resultset": "catalog",
            }
        )
        return self.fetch_data(params=params)

    def get_card(self, product: Product):
        """
        Запрос за характеристиками и описанием товара
        """
        card_url = f"https://basket-{product.basket_num}.wbbasket.ru/vol{product.vol}/part{product.part}/{product.product_id}/info/ru/card.json"
        return self.fetch_data(url=card_url, params={})
