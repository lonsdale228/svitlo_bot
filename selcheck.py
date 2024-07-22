import time
import webbrowser
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, Page

from undetected_playwright import Tarnished


def cache_screenshot(page: Page):
    _now = datetime.now().strftime("%Y-%m-%d")
    _suffix = f"-view-new-{datetime.now().strftime('%H%M%S')}"
    path = f"result/{_now}/sannysoft{_suffix}.png"
    page.screenshot(path=path, full_page=True)

    webbrowser.open(f"file://{Path(path).resolve()}")


def main():
    args = []

    with sync_playwright() as p:
        browser = p.chromium.launch(args=args)
        context = browser.new_context(locale="en-US")

        # Injecting Context
        Tarnished.apply_stealth(context)
        page = context.new_page()

        while True:
            page.goto("https://www.dtek-oem.com.ua/ua/shutdowns", wait_until="networkidle")

            page.wait_for_selector('//*[@id="city"]')

            page.fill('//*[@id="city"]', 'с. Лиманка')
            page.wait_for_selector('//*[@id="cityautocomplete-list"]/div')
            page.click('//*[@id="cityautocomplete-list"]/div[1]')

            page.fill('//*[@id="street"]', 'вул. Затишна')
            page.wait_for_selector('//*[@id="streetautocomplete-list"]/div[1]')
            page.click('//*[@id="streetautocomplete-list"]/div[1]')

            page.fill('//*[@id="house_num"]', '10')
            page.wait_for_selector('//*[@id="house_numautocomplete-list"]/div[1]')
            page.click('//*[@id="house_numautocomplete-list"]/div[1]')

            text = page.inner_text('//*[@id="showCurOutage"]/p/strong[3]')
            print(text)
            time.sleep(10)

        # cache_screenshot(page)
        # time.sleep(10)

        browser.close()


if __name__ == "__main__":
    main()
