import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--lang=ru-RU')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 1. Заходим на страницу новостей
driver.get("https://ru.investing.com/news")
time.sleep(3)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

articles = soup.find_all("article")[:3]
news_data = []

for article in articles:
    link_tag = article.find("a", href=True)
    if not link_tag:
        continue

    title = link_tag.get_text(strip=True)
    link = link_tag["href"]

    if link.startswith("http"):
        full_url = link
    else:
        full_url = "https://ru.investing.com" + link

    # 2. Переход внутрь статьи
    driver2 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver2.get(full_url)
    time.sleep(3)

    try:
        article_div = WebDriverWait(driver2, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='article']"))
        )
        paragraphs = article_div.find_elements(By.TAG_NAME, "p")
        article_text = "\n".join([p.text for p in paragraphs if p.text.strip()])

        news_data.append({
            "url": full_url,
            "title": title,
            "text": article_text
        })

    except Exception as e:
        print("❌ Ошибка:", full_url, e)

    driver2.quit()

driver.quit()

# создаём датафрейм
df = pd.DataFrame(news_data)

# сортировка по заголовку (пример)
df = df.sort_values(by="title")

print(df.head())

# сохраняем для LLM
df.to_csv("news_dataset.csv", index=False, encoding="utf-8-sig")
