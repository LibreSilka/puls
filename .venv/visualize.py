import pandas as pd
import json
import plotly.express as px

companies_data = [
    # Аэрокосмическая промышленность
    ['Аэрокосмическая промышленность', 'ОАК', 608],
    ['Аэрокосмическая промышленность', 'Яковлев (Иркут)', 351],
    ['Аэрокосмическая промышленность', 'Аэрофлот', 247],

    # Металлы и добыча
    ['Металлы и добыча', 'Полюс', 3206],
    ['Металлы и добыча', 'ГМК Норникель', 1973],
    ['Металлы и добыча', 'Северсталь', 891],
    ['Металлы и добыча', 'НЛМК', 706],
    ['Металлы и добыча', 'Русал', 523],
    ['Металлы и добыча', 'ВСМПО-АВИСМА', 396],
    ['Металлы и добыча', 'ММК', 368],
    ['Металлы и добыча', 'АЛРОСА', 350],
    ['Металлы и добыча', 'En+', 288],
    ['Металлы и добыча', 'Полиметалл', 242],
    ['Металлы и добыча', 'Южуралзолото', 142],
    ['Металлы и добыча', 'Распадская', 142],

    # Нефть и газ
    ['Нефть и газ', 'Роснефть', 4895],
    ['Нефть и газ', 'Лукойл', 4544],
    ['Нефть и газ', 'НОВАТЭК', 3710],
    ['Нефть и газ', 'Газпром', 3066],
    ['Нефть и газ', 'Газпромнефть', 2507],
    ['Нефть и газ', 'Татнефть', 1528],
    ['Нефть и газ', 'Сургутнефтегаз', 1164],
    ['Нефть и газ', 'Транснефть', 902],
    ['Нефть и газ', 'Башнефть', 279],

    # Пищевая промышленность
    ['Пищевая промышленность', 'Черкизово', 150],

    # Промышленность
    ['Промышленность', 'ДВМП', 175],

    # Ритейл
    ['Ритейл', 'X5 Group', 791],
    ['Ритейл', 'Магнит', 353],
    ['Ритейл', 'Лента', 211],

    # Строительство
    ['Строительство', 'ПИК', 414],

    # Телеком
    ['Телеком', 'МТС', 439],
    ['Телеком', 'Ростелеком', 236],

    # Технологии
    ['Технологии', 'Яндекс', 1670],
    ['Технологии', 'ОЗОН', 941],
    ['Технологии', 'HeadHunter', 182],

    # Транспорт
    ['Транспорт', 'Совкомфлот', 209],
    ['Транспорт', 'НМТП', 171],

    # Финансы
    ['Финансы', 'Сбербанк', 6967],
    ['Финансы', 'ВТБ', 935],
    ['Финансы', 'Тинькофф', 876],
    ['Финансы', 'Московская биржа', 400],
    ['Финансы', 'Совкомбанк', 330],
    ['Финансы', 'МКБ', 267],
    ['Финансы', 'Банк Санкт-Петербург', 167],
    ['Финансы', 'Росбанк', 158],
    ['Финансы', 'АФК Система', 154],

    # Химия и удобрения
    ['Химия и удобрения', 'ФосАгро', 930],
    ['Химия и удобрения', 'Акрон', 605],
    ['Химия и удобрения', 'НКНХ', 156],

    # Энергетика
    ['Энергетика', 'ИнтерРАО', 331],
    ['Энергетика', 'Русгидро', 207],
    ['Энергетика', 'Россети Ленэнерго', 167],
    ['Энергетика', 'Россети (ФСК)', 153],
]

companies = pd.DataFrame(companies_data, columns=['sector', 'issuer', 'market_cap'])
companies['summary'] = ''
companies['link'] = ''
companies['influence'] = 'neutral'
companies['strength'] = 0



def load_llm_json(llm_result):
    """
    Загружает JSON с результатом LLM (уже чистый массив словарей)
    и возвращает список словарей.
    """
    with open(llm_result, encoding='utf-8') as f:
        influence_list = json.load(f)
    return influence_list


def apply_llm_to_companies(companies_df, influence_list):
    df = companies_df.copy()
    for entry in influence_list:
        issuer_llm = entry['эмитент'].strip().lower()
        # ищем в названиях компаний по вхождению (подстроке)
        mask = df['issuer'].str.lower().str.contains(issuer_llm, na=False)

        if mask.any():  # только если нашли совпадение
            df.loc[mask, 'influence'] = entry['влияние']
            df.loc[mask, 'strength'] = float(entry['сила влияния'])
            df.loc[mask, 'summary'] = entry['краткий вывод']
            df.loc[mask, 'link'] = entry['ссылка']
    return df

influence_list = load_llm_json("llm_result.json")
companies = apply_llm_to_companies(companies, influence_list)
# мап для численной окраски
direction_map = {"positive": 1, "negative": -1, "neutral": 0}
companies['dir_num'] = companies['influence'].map(direction_map)
companies['heat'] = companies['dir_num'] * companies['strength']

color_scale = [
    [0, "red"],
    [0.5, "white"],
    [1, "green"]
]

fig = px.treemap(
    companies,
    path=["sector", "issuer"],
    values="market_cap",
    color="heat",
    color_continuous_scale=color_scale,
    range_color=[-1, 1],
    hover_data={
        "summary": True,
        "link": True,
        "market_cap": True,
        "strength": True
    }
)

fig.update_traces(
    hovertemplate="<b>%{label}</b><br>Сектор: %{parent}<br>Капитализация: %{customdata[2]}<br>Влияние: %{color:.2f}<br>Сила: %{customdata[3]:.2f}<br>Кратко: %{customdata[0]}<br><a href='%{customdata[1]}'>ссылка на новость</a><extra></extra>"
)

fig.update_layout(margin=dict(t=60, l=0, r=0, b=0), title="Новости и влияние на компании Мосбиржи")
fig.write_html("moex_top50_dynamic_heatmap.html")
print("Файл готов: moex_top50_dynamic_heatmap.html")
