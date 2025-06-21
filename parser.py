"""
🔧 Название: Avito Parser 
📁 Файл: parser.py
👤 Автор: Metiso4kas
📅 Июнь 2025
💼 Назначение: Парсинг Avito 
🛡 Лицензия: MIT

## 📜 Отказ от ответственности

- 🛠️ Данный проект создан исключительно для учебных и ознакомительных целей.
- 🏢 Он не является официальным продуктом Avito и не связан с администрацией сайта [Avito.ru](https://www.avito.ru).
- ⚠️ Использование данного парсера может противоречить **условиям обслуживания Avito.
- 👤 Автор проекта не несёт ответственности за любые последствия использования этого инструмента.
- ❌ Коммерческое использование, массовый сбор данных и автоматизированная перепродажа информации строго запрещены."
"""
import time
import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from config import PROXY, HEADLESS, SEARCH_PAGES

CITY_SLUG_MAP = {
    "moskva": "Москва",
    "sankt-peterburg": "Санкт-Петербург",
    "novosibirsk": "Новосибирск",
    "ekaterinburg": "Екатеринбург",
    "kazan": "Казань",
    "rostov-na-donu": "Ростов-на-Дону",
    "nizhniy_novgorod": "Нижний Новгород",
    "chelyabinsk": "Челябинск",
    "samara": "Самара",
    "ufa": "Уфа",
    "krasnoyarsk": "Красноярск",
    "perm": "Пермь",
    "voronezh": "Воронеж",
    "volgograd": "Волгоград",
    "omsk": "Омск",
    "podolsk": "Подольск",
    "rossiya": "Россия"
}

def slug_to_city(slug):
    return CITY_SLUG_MAP.get(slug.lower(), slug.replace("-", " ").title())

def run_parser(query, city="rossiya"):
    options = uc.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument(f"user-agent={UserAgent().random}")
    if PROXY:
        options.add_argument(f"--proxy-server=http://{PROXY}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)
    results = []

    base_url = "https://www.avito.ru/rossiya"
    query_url = f"{base_url}?q={query}"

    try:
        for page in range(1, SEARCH_PAGES + 1):
            url = f"{query_url}&p={page}"
            print(f"🌐 Открытие страницы {page}: {url}")
            driver.get(url)
            time.sleep(2)

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-marker="item"]'))
            )

            items = driver.find_elements(By.CSS_SELECTOR, 'div[data-marker="item"]')
            print(f"📦 Найдено объявлений: {len(items)}")

            for item in items:
                try:
                    title_el = item.find_element(By.CSS_SELECTOR, '[data-marker="item-title"]')
                    price_el = item.find_element(By.CSS_SELECTOR, '[data-marker="item-price"]')

                    try:
                        loc_el = item.find_element(By.CSS_SELECTOR, '[data-marker="item-address"]')
                        location = loc_el.text
                        city = location.split(',')[0].strip()
                    except:
                        location = "—"
                        city = "—"

                    try:
                        link_el = item.find_element(By.CSS_SELECTOR, 'a[data-marker="item-title"]')
                        link = link_el.get_attribute("href")
                        slug = link.split("/")[3]
                        city = slug_to_city(slug)
                    except:
                        link = "—"

                    results.append({
                        "Название": title_el.text,
                        "Цена": price_el.text,
                        "Город": city,
                        "Ссылка": link
                    })

                except Exception as e:
                    print(f"⚠️ Ошибка парсинга элемента: {e}")

            time.sleep(2)
    finally:
        driver.quit()
        del driver

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv("data/results.csv", index=False, encoding="utf-8-sig")
    print(f"✅ Парсинг завершён! Сохранено {len(df)} объявлений.")
