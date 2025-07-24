from dotenv import load_dotenv
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO
import logging
from collections import Counter
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPID_API_KEY")
API_URL = "https://rapid-translate-multi-traduction.p.rapidapi.com/t"

HEADERS = {
    "Content-Type": "application/json",
    "x-rapidapi-host": "rapid-translate-multi-traduction.p.rapidapi.com",
    "x-rapidapi-key": RAPIDAPI_KEY,
}

# Translation function
def translate_text(text, from_lang="es", to_lang="en"):
    payload = {
        "from": from_lang,
        "to": to_lang,
        "q": text,
    }

    response = requests.post(API_URL, json=payload, headers=HEADERS)

    response.raise_for_status()

    return response.json()[0]

# Set up browser
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://elpais.com/")
time.sleep(2)

# Hide overlay if present
try:
    overlay = driver.find_element(By.CLASS_NAME, "blockNavigation")
    driver.execute_script("arguments[0].style.display='none';", overlay)
    logging.info("Overlay hidden")
except:
    logging.info("No overlay found")

# Navigate to Opinión section
try:
    opinion_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/opinion/')]"))
    )
    ActionChains(driver).move_to_element(opinion_link).click().perform()
    logging.info("Navigated to Opinión section!")
except:
    logging.error("Failed to click on Opinión link")
    driver.quit()
    exit()

time.sleep(3)

# Find article links
article_links = []
seen = set()

articles = driver.find_elements(By.XPATH, "//a[contains(@href, '/opinion/') and contains(@href, '.html') and starts-with(@href, 'https://')]")
for a in articles:
    href = a.get_attribute("href")
    if href and href not in seen and not href.endswith('/opinion/'):
        seen.add(href)
        article_links.append(href)
    if len(article_links) == 5:
        break

os.makedirs("images", exist_ok=True)

print("\n📰 Article Details:\n")
titles = []

for i, link in enumerate(article_links, 1):
    driver.get(link)
    time.sleep(2)

    # Cookie Window if present
    try:
        accept_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceptar') or contains(., 'Accept')]"))
        )
        accept_btn.click()
        logging.info("Cookie consent accepted")
        time.sleep(1)
    except:
        pass

    try:
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        ).text.strip()
        titles.append(title)
    except:
        title = "[No Title Found]"
        print(f"{i}. Warning: No title found for {link}")
        continue

    try:
        paragraphs = driver.find_elements(By.XPATH, "//div[contains(@class,'article_body')]//p | //article//p")
        content = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
    except:
        content = "[No Content Found]"

    img_status = "No image found"
    try:
        try:
            og_img = driver.find_element(By.XPATH, "//meta[@property='og:image']")
            img_url = og_img.get_attribute("content")
        except:
            img_url = None

        if not img_url:
            img_element = driver.find_element(By.XPATH, "//figure//img | //picture//img | //img")
            img_url = img_element.get_attribute("src")

        if img_url and img_url.startswith("http"):
            img_data = requests.get(img_url).content
            image = Image.open(BytesIO(img_data))

            if image.width >= 100 and image.height >= 100:
                filename = f"images/article_{i}.jpg"
                with open(filename, "wb") as f:
                    f.write(img_data)
                img_status = f"✅ Image saved as {filename}"
    except Exception as e:
        img_status = f"Image error ({e})"

    print(f"{i}. 📰 {title}\n")
    print(content[:700] + "...\n")
    print(img_status)
    print("-" * 60)

driver.quit()

# Translate and Print Titles
translated_titles = []
print("\n Translated Titles:")
for idx, title in enumerate(titles, 1):
    translated = translate_text(title)
    translated_titles.append(translated)
    print(f"{idx}. {title}")
    print(f"    → {translated}\n")

# Analyze Repeated Words
# Normalize words (lowercase & remove punctuation)
all_words = []
for line in translated_titles:
    words = re.findall(r"\b\w+\b", line.lower())
    all_words.extend(words)

# Count frequency
word_counts = Counter(all_words)

# Filter repeated words (more than twice)
repeated_words = {word: count for word, count in word_counts.items() if count > 2}

# Print result
print("\n Repeated Words (more than twice):")
if repeated_words:
    for word, count in repeated_words.items():
        print(f"{word}: {count}")
else:
    print("  No words repeated more than twice.")