import os
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Инвестиционный Портфель (Финам)", layout="wide")
st.title("📊 Мониторинг портфеля Финам в реальном времени")

# Запрос пароля для доступа
password = st.text_input("Введите пароль для просмотра:", type="password")
VALID_PASSWORD = os.environ.get("VIEWER_PASSWORD", "12345")

if password == VALID_PASSWORD:
    st.success("Доступ разрешен")
    
    if st.button("🔄 Обновить данные"):
        st.rerun()

    TOKEN = os.environ.get("FINAM_TOKEN")
    CLIENT_ID = os.environ.get("FINAM_CLIENT_ID")

    if not TOKEN or not CLIENT_ID:
        st.error("Ошибка: FINAM_TOKEN или FINAM_CLIENT_ID не найдены в Secrets.")
    else:
        try:
            url = f"https://trade-api.finam.ru/api/v1/portfolio?clientId={CLIENT_ID}&includePositions=true&includeMaxBuySell=true"
            headers = {
                "X-Api-Key": TOKEN,
                "accept": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
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

                # Показываем балансовые показатели
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
            else:
                st.error(f"Ошибка сервера Финам (Код {response.status_code}): {response.text}")

        except Exception as e:
            st.error(f"Произошла ошибка при обработке данных: {e}")

elif password != "":
    st.error("Неверный пароль")
