from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')  # без интерфейса
options.add_argument('--disable-gpu')
options.add_argument('--lang=ru-RU')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.1 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)



driver.get("https://ru.investing.com/news/world-news/article-2904830")
time.sleep(3)

article_div = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, "//*[@id='article']"))
)
# Собираем все параграфы внутри
paragraphs = article_div.find_elements(By.TAG_NAME, "p")

# Склеиваем в один текст
article_text = "\n".join([p.text for p in paragraphs if p.text.strip()])
print(article_text)

driver.quit()