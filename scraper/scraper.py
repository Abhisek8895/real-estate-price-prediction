from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# start chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

url = "https://www.magicbricks.com/property-for-sale-in-bhubaneswar-pppfs"

driver.get(url)

time.sleep(5)

properties = driver.find_elements(By.CLASS_NAME, "mb-srp__card")

data = []

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

    data.append({
        "price": price,
        "title": title,
        "area": area
    })

driver.quit()

df = pd.DataFrame(data)

print(df.head())
print("Total properties scraped:", len(df))

df.to_csv("properties.csv", index=False)

print("Data saved successfully")