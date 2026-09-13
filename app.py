import os
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Инвестиционный Портфель (Финам)", layout="wide")
st.title("📊 Мониторинг портфеля Финам в реальном времени")

password = st.text_input("Введите пароль для просмотра:", type="password")
VALID_PASSWORD = os.environ.get("VIEWER_PASSWORD", "12345")

if password == VALID_PASSWORD:
    st.success("Доступ разрешен")
    
    if st.button("🔄 Обновить данные"):
        st.rerun()

    TOKEN = os.environ.get("FINAM_TOKEN")
    CLIENT_ID = os.environ.get("FINAM_CLIENT_ID")

    if not TOKEN:
        st.error("Ошибка: FINAM_TOKEN не найден в Secrets.")
    else:
        # Подготовка заголовков
        headers = {
            "X-Api-Key": TOKEN.strip(),
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # 1. Если CLIENT_ID не задан, сначала выводим список счетов
        if not CLIENT_ID:
            st.warning("Укажите FINAM_CLIENT_ID в Secrets. Получаем доступные счета...")
            res = requests.get("https://trade-api.finam.ru/api/v1/user", headers=headers)
            if res.status_code == 200:
                st.json(res.json())
            else:
                st.error(f"Ошибка получения профиля (Код {res.status_code}): {res.text}")
        else:
            # 2. Получение портфеля
            url = f"https://trade-api.finam.ru/api/v1/portfolio?clientId={CLIENT_ID.strip()}&includePositions=true&includeMaxBuySell=true"
            res = requests.get(url, headers=headers)

            if res.status_code == 200:
                try:
                    data = res.json()
                    positions = data.get("positions", [])
                    
                    positions_data = []
                    for pos in positions:
                        positions_data.append({
                            "Инструмент": pos.get("securityCode", "—"),
                            "Рынок": pos.get("market", "—"),
                            "Количество": pos.get("balance", 0),
                            "Текущая цена": pos.get("currentPrice", 0),
                            "Средняя цена": pos.get("averagePrice", 0),
                            "P&L (Прибыль/Убыток)": pos.get("unrealizedProfit", 0)
                        })

                    currencies = data.get("currencies", [])
                    if currencies:
                        st.subheader("💰 Баланс и Маржа")
                        st.json(currencies)

                    if positions_data:
                        df = pd.DataFrame(positions_data)
                        st.subheader("📈 Открытые позиции (включая Фьючерсы)")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("Открытые позиции отсутствуют или портфель пуст.")
                except Exception as json_err:
                    st.error(f"Ошибка разбора ответа: {json_err}. Ответ сервера: {res.text}")
            else:
                st.error(f"Ошибка сервера Финам (Код {res.status_code}): {res.text}")

elif password != "":
    st.error("Неверный пароль")
