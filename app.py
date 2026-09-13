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
        # Убираем лишние пробелы из токена и ID
        token_clean = TOKEN.strip()
        client_clean = CLIENT_ID.strip() if CLIENT_ID else ""

        # Для Trade API Финам токен передаётся как через X-Api-Key, так и через Authorization
        headers = {
            "X-Api-Key": token_clean,
            "Authorization": f"Bearer {token_clean}",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        # Выполняем запрос к v1/portfolio
        url = f"https://trade-api.finam.ru/api/v1/portfolio"
        params = {
            "clientId": client_clean,
            "includePositions": "true",
            "includeMaxBuySell": "true"
        }

        try:
            res = requests.get(url, headers=headers, params=params)

            if res.status_code == 200:
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
                    st.subheader("💰 Баланс / Маржа")
                    st.json(currencies)

                if positions_data:
                    df = pd.DataFrame(positions_data)
                    st.subheader("📈 Открытые позиции (включая Фьючерсы)")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Открытые позиции отсутствуют или портфель пуст.")
            else:
                st.error(f"Сервер Финам вернул статус {res.status_code}.")
                st.code(res.text[:500], language="text")

        except Exception as e:
            st.error(f"Ошибка запроса: {e}")

elif password != "":
    st.error("Неверный пароль")
