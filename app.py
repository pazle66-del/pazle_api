import os
import pandas as pd
import streamlit as st
from finam_trade_api.client import Client

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
    CLIENT_ID = os.environ.get("FINAM_CLIENT_ID")  # Торговый код счета (например, 123456R...)

    if not TOKEN or not CLIENT_ID:
        st.error("Ошибка: FINAM_TOKEN или FINAM_CLIENT_ID не найдены в настройках Secrets.")
    else:
        try:
            client = Client(TOKEN)
            portfolio = client.get_portfolio(CLIENT_ID)

            positions_data = []

            # Перебираем позиции в портфеле (включая срочный рынок / фьючерсы)
            if hasattr(portfolio, 'positions') and portfolio.positions:
                for pos in portfolio.positions:
                    security_code = getattr(pos, 'security_code', '—')
                    market = getattr(pos, 'market', '—')
                    balance = getattr(pos, 'balance', 0)
                    price = getattr(pos, 'current_price', 0)
                    average_price = getattr(pos, 'average_price', 0)
                    unrealized_profit = getattr(pos, 'unrealized_profit', 0)

                    positions_data.append({
                        "Инструмент": security_code,
                        "Рынок": market,
                        "Количество": balance,
                        "Текущая цена": f"{price:.2f}" if isinstance(price, (int, float)) else price,
                        "Средняя цена": f"{average_price:.2f}" if isinstance(average_price, (int, float)) else average_price,
                        "P&L (Прибыль/Убыток)": f"{unrealized_profit:.2f}" if isinstance(unrealized_profit, (int, float)) else unrealized_profit
                    })

            if positions_data:
                df = pd.DataFrame(positions_data)
                st.subheader("Открытые позиции (включая Фьючерсы)")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Портфель пуст или активные позиции отсутствуют.")

        except Exception as e:
            st.error(f"Ошибка при получении данных от Финам Trade API: {e}")

elif password != "":
    st.error("Неверный пароль")
