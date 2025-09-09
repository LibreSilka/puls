import pandas as pd
from llama_cpp import Llama
import json

# Укажи путь к своему gguf-файлу модели (обычно это .gguf)
MODEL_PATH = r"C:\Users\n.khrobostov\.lmstudio\models\lmstudio-community\DeepSeek-R1-0528-Qwen3-8B-GGUF\DeepSeek-R1-0528-Qwen3-8B-Q4_K_M.gguf"

# Настроим Llama (число токенов и прочее можно менять)
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=3,temperature=0.1,top_p=0.8,repeat_penalty=1.1, verbose=False)

def make_prompt(title, text):
    prompt = f"""
Ты — финансовый аналитик. 
Ответь строго в формате JSON. Не добавляй комментариев, текста вне JSON.

Формат ответа:
{{
  "title": "...",
  "sentiment": "positive|negative|neutral",
  "impact": "low|medium|high",
  "reason": "..."
}}

Заголовок: {row['title']}
Текст: {row['text'][:1000]}
"""
    return prompt

df = pd.read_csv("news_dataset.csv")
results = []

for idx, row in df.iterrows():
    prompt = make_prompt(row['title'], row['text'][:1000])  # если новость очень длинная — обрезаем текст
    output = llm(
        prompt,
        max_tokens=256,
    )
    answer = output["choices"][0]["text"].strip()
    print(answer)
    try:
        json_start = answer.find('{')
        json_end = answer.rfind('}') + 1
        res = json.loads(answer[json_start:json_end])
        results.append({**row, **res})
    except Exception as e:
        print(f"[{idx}] Ошибка парсинга ответа LLM:", e)
        results.append({**row, "error": str(e), "llm_raw": answer})

df_llm = pd.DataFrame(results)
df_llm.to_csv("news_with_llama_impact.csv", index=False, encoding="utf-8-sig")