from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Настройки Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # без интерфейса
options.add_argument('--disable-gpu')
options.add_argument('--lang=ru-RU')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.1 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 1. Заходим на страницу новостей
driver.get("https://ru.investing.com/news")
time.sleep(3)  # ждём загрузку js

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# 2. Собираем статьи
articles = soup.find_all("article")
news=[]

for idx, article in enumerate(articles, start=1):
    link_tag = article.find("a", href=True)
    if not link_tag:
        continue

    title = link_tag.get_text(strip=True)
    link = link_tag["href"]

    # Проверяем полный/относительный URL
    if link.startswith("http"):
        full_url = link
    else:
        full_url = "https://ru.investing.com" + link

    news.append(full_url)
    # print(f"\n=== Новость {idx} ===")
    # print("Заголовок:", title)
    # print("Ссылка:", full_url)
print(news)
driver.quit()

for i in news:
    # 3. Переходим в новость
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(i)
    time.sleep(3)

    try:
        article_div = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='article']"))
        )

        # Собираем все параграфы внутри
        paragraphs = article_div.find_elements(By.TAG_NAME, "p")

        # Склеиваем в один текст
        article_text = "\n".join([p.text for p in paragraphs if p.text.strip()])
        print(article_text)

    except Exception as e:
        print("❌ Текст не найден:",i,e)

