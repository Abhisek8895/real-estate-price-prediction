from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
import pandas as pd
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

all_data = []

for page in range(1, 60):

    url = f"https://www.magicbricks.com/property-for-sale-in-bhubaneswar-pppfs/page-{page}"

    print(f"Scraping page {page}")

    driver.get(url)

    time.sleep(5)

    properties = driver.find_elements(By.CLASS_NAME, "mb-srp__card")

    for prop in properties:

        try:
            price = prop.find_element(By.CLASS_NAME, "mb-srp__card__price").text
        except:
            price = None

        try:
            title = prop.find_element(By.CLASS_NAME, "mb-srp__card--title").text
        except:
            title = None

        try:
            area = prop.find_element(By.CLASS_NAME, "mb-srp__card__summary").text
        except:
            area = None

        all_data.append({
            "price": price,
            "title": title,
            "area": area
        })

driver.quit()

df = pd.DataFrame(all_data)

print("Total properties scraped:", len(df))

df.to_csv("../data/properties.csv",index=False, encoding="utf-8-sig")