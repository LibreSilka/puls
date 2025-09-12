import requests
import pandas as pd
import json
from s import YANDEX_API_KEY


# Загружаем новости
df = pd.read_csv("news_dataset.csv")

# Берем первые 3 новости для примера
sample_news = df.head(3).to_dict(orient="records")

# Формируем JSON-строку с новостями
news_json = json.dumps(sample_news, ensure_ascii=False, indent=2)

# Промпт
prompt = {
  "modelUri": "gpt://b1ghtfo1op8535f5pjc3/yandexgpt-lite",
  "completionOptions": {
    "stream": False,
    "temperature": 0.6,
    "maxTokens": "2000",
    "reasoningOptions": {
      "mode": "DISABLED"
    }
  },
  "messages": [
    {
      "role": "system",
      "text": "Ты — финансовый аналитик, настоящий эксперт своего дела, видишь всю картину целком. Проанализируй новости(они могу содержать в себе лишнюю информацию по типу рекламы или названий других статей, т.к. парсились с сайта), сделай краткий вывод, содержащий аргументацию твоей оценки(не более 2-3 предложений). Оценивай очень внимательно, предполагай как и на какие сектора может повлиять новость. Верни JSON с ключами: сектор, эмитент, влияние (positive/negative/neutral), сила влияния (от 0 до 1), краткий вывод, ссылка"
    },
    {
      "role": "user",
      "text": f"Вот новости для анализа:\n{news_json}"
    }
  ]
}


url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
headers = {
    'Content-Type': 'application/json',
    'Authorization': YANDEX_API_KEY
}

response = requests.post(url, headers=headers, json=prompt)
result = response.json()
text = result["result"]["alternatives"][0]["message"]["text"]

# 2. Убираем ``` и лишние переносы
clean_text = text.strip().strip("`").replace("```json", "").replace("```", "").strip()

# 3. Преобразуем в Python-объект
try:
    parsed = json.loads(clean_text)
except json.JSONDecodeError as e:
    print("Ошибка парсинга JSON:", e)
    parsed = []

# 4. Сохраняем в файл
with open("llm_result2.json", "w", encoding="utf-8") as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)

print("✅ Результат сохранен в llm_result.json")


