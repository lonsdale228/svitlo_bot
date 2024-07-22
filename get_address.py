import time

# import chromedriver_autoinstaller
# chromedriver_autoinstaller.install()
import undetected_chromedriver as uc
driver = uc.Chrome(headless=True,use_subprocess=False)
driver.get("https://www.dtek-oem.com.ua/ua/shutdowns")
time.sleep(100)