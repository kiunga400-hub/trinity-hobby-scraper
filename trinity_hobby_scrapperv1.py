import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

BASE_URL = "https://trinityhobby.com/collections/trading-cards/yugioh?usf_sort=bestselling"
url = "https://trinityhobby.com"

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# closing popup
driver.get(BASE_URL)
shadow_host = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "shopify-forms-embed"))
)
shadow_root = driver.execute_script(
    "return arguments[0].shadowRoot", shadow_host
)
close_button = shadow_root.find_element(
    By.CSS_SELECTOR, 'span[aria-label="Close modal"]'
)
close_button.click()

all_product = []

while True:

    # rebuild soup for current page
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    links = soup.find_all("div", class_="usf-sr-product usf-grid__item")

    for block in links:
        refresh_dic = {}

        href = block.find("a")["href"]
        driver.get(url + href)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product__title"))
        )

        page_source = driver.page_source
        inside_soup = BeautifulSoup(page_source, "html.parser")

        title = inside_soup.find("h1", class_="product__title").get_text(strip=True)

        price_box = inside_soup.find("span", class_="f-price-item f-price-item--regular")
        price = price_box.find("span", class_="money").get_text(strip=True)

        refresh_dic["title"] = title
        refresh_dic["price"] = price
        refresh_dic["link"] = url + href

        all_product.append(refresh_dic)

        # go back to listing page
        driver.back()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".usf-sr-product"))
        )

    # try go next page
    try:
        next_page = driver.find_element(By.CSS_SELECTOR, "li.usf-sr-pages__next a")
        next_page.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".usf-sr-product"))
        )

    except NoSuchElementException:
        break  # no more pages

# save JSON
with open("TrinityHobby.json", "w", encoding="utf-8") as file:
    json.dump(all_product, file, indent=4, ensure_ascii=False)

print(f"Scraped {len(all_product)} products")

driver.quit()