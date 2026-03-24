import time

import undetected_chromedriver as uc

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0"
URL = "https://www.wildberries.ru/"
COOKIE_NEED = "x_wbaas_token"


class WebdriverCookies:
    """
    Класс для получения токена x_wbaas_token
    """

    def __init__(
        self, user_agent: str = None, url: str = None, cookie_need: str = None
    ):
        self.user_agent = user_agent or USER_AGENT
        self.url = url or URL
        self.cookie_need = cookie_need or COOKIE_NEED
        self.SLEEP_TIME = 5

    def get_token(self) -> str:
        driver = uc.Chrome()
        try:
            driver.get(self.url)
            for i in range(3):
                cookies = driver.execute_cdp_cmd("Network.getAllCookies", {})
                for cookie in cookies.get("cookies"):
                    if cookie.get("name") == self.cookie_need:
                        print("Куки получены")
                        return cookie.get("value")
                time.sleep(self.SLEEP_TIME)
            return None
        finally:
            driver.quit()


def get_token() -> str:
    """
    Получаем актуальный токен для Wildberries
    """
    return WebdriverCookies().get_token()
