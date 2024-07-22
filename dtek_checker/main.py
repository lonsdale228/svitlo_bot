import random
import time
from datetime import datetime
import pytz
import redis
from playwright.sync_api import sync_playwright, Page
from undetected_playwright import Tarnished

r = redis.from_url("redis://redis", encoding="utf8")
kyiv_tz = pytz.timezone('Europe/Kiev')

r.set('last_script_update', str(datetime.now(tz=kyiv_tz)))


def main():
    args = ["--headless"]

    with sync_playwright() as p:
        browser = p.chromium.launch(args=args)
        context = browser.new_context(locale="en-US")

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

            on_at = page.inner_text('//*[@id="showCurOutage"]/p/strong[3]')
            reason = page.inner_text('//*[@id="showCurOutage"]/p/strong[1]')
            start_time = page.inner_text('//*[@id="showCurOutage"]/p/strong[2]')
            # last_update_time = page.inner_text('//*[@id="showCurOutage"]/p/text()[5]')
            group_number = page.inner_text('//*[@id="group-name"]/span')

            last_update_time = page.evaluate('''
                        () => {
                            const element = document.querySelector('#showCurOutage > p');
                            const textNodes = Array.from(element.childNodes).filter(node => node.nodeType === Node.TEXT_NODE);
                            return textNodes[textNodes.length - 1].textContent.trim();
                        }
                    ''')

            data = {
                "disable_reason": reason,
                "on_at": on_at,
                "start_time": start_time,
                "last_dtek_update": last_update_time,
                "group_number": group_number
            }
            r.mset(data)

            print(on_at)
            time.sleep(random.randint(10, 60))

        browser.close()


if __name__ == "__main__":
    main()
