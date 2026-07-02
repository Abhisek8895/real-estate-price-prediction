from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
import pandas as pd
import re
import json
import os
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

OUTPUT_PATH = "../data/properties.csv"
seen_ids = set()

if os.path.exists(OUTPUT_PATH):
    existing = pd.read_csv(OUTPUT_PATH)
    seen_ids = set(existing["id"].astype(str))

def extract_json_blob(html):
    match = re.search(r"window\.SERVER_PRELOADED_STATE_\s*=\s*(\{.*?\});\s*</script>", html, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

def parse_property(p):
    return {
        "id": p.get("id"),
        "title": p.get("propertyTitle"),
        "price": p.get("price"),
        "price_display": p.get("priceD"),
        "price_per_sqft": p.get("sqFtPrice"),
        "locality": p.get("lmtDName"),
        "city": p.get("ctName"),
        "bhk": p.get("bedroomD"),
        "bathrooms": p.get("bathD"),
        "balconies": p.get("balconiesD"),
        "area_sqft": p.get("caSqFt") or p.get("coveredArea"),
        "carpet_area": p.get("carpetArea"),
        "furnishing": p.get("furnishedD"),
        "floor": p.get("floorD"),
        "transaction_type": p.get("transactionTypeD"),
        "property_type": p.get("propTypeD"),
        "possession_status": p.get("possStatusD"),
        "ownership": p.get("OwnershipTypeD"),
        "facing": p.get("facingD"),
        "society": p.get("prjname"),
        "posted_by": p.get("userType"),
        "url": "https://www.magicbricks.com/" + str(p.get("seoURL")) if p.get("seoURL") else None,
    }

for page in range(1, 60):
    url = f"https://www.magicbricks.com/property-for-sale-in-bhubaneswar-pppfs/page-{page}"
    print(f"Scraping page {page}")
    driver.get(url)

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mb-srp__card")))
    except:
        print(f"No cards found on page {page}, stopping")
        break

    html = driver.page_source
    data = extract_json_blob(html)

    if not data or "searchResult" not in data or not data["searchResult"]:
        print(f"No JSON data found on page {page}, stopping")
        break

    page_rows = []
    for prop in data["searchResult"]:
        prop_id = str(prop.get("id"))
        if prop_id in seen_ids:
            continue
        page_rows.append(parse_property(prop))
        seen_ids.add(prop_id)

    if page_rows:
        df_page = pd.DataFrame(page_rows)
        header = not os.path.exists(OUTPUT_PATH)
        df_page.to_csv(OUTPUT_PATH, mode="a", header=header, index=False, encoding="utf-8-sig")

    time.sleep(2)

driver.quit()
print("Done. Total unique properties:", len(seen_ids))