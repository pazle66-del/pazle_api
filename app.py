import os
import pandas as pd
import streamlit as st
from tinkoff.invest import Client

st.set_page_config(page_title="Инвестиционный Портфель", layout="wide")
st.title("📊 Мониторинг портфеля в реальном времени")

# Запрос пароля для доступа
password = st.text_input("Введите пароль для просмотра:", type="password")
VALID_PASSWORD = os.environ.get("VIEWER_PASSWORD", "12345")

if password == VALID_PASSWORD:
    st.success("Доступ разрешен")
    
    if st.button("🔄 Обновить данные"):
        st.rerun()

    TOKEN = os.environ.get("INVEST_TOKEN")

    if not TOKEN:
        st.error(" Ошибка: API-токен не найден в настройках Streamlit.")
    else:
        try:
            with Client(TOKEN) as client:
                accounts = client.users.get_accounts().accounts
                if not accounts:
                    st.warning("Счета не найдены.")
                else:
                    account_id = accounts[0].id
                    portfolio = client.operations.get_portfolio(account_id=account_id)

                    positions_data = []

                    for pos in portfolio.positions:
                        instrument_type = pos.instrument_type
                        figi = pos.figi
                        
                        quantity = float(pos.quantity.units + pos.quantity.nano / 1e9) if pos.quantity else 0
                        price = float(pos.current_price.units + pos.current_price.nano / 1e9) if pos.current_price else 0
                        
                        total_value = quantity * price

                        positions_data.append({
                            "Тип": instrument_type.upper(),
                            "FIGI / Идентификатор": figi,
                            "Количество": quantity,
                            "Текущая цена": f"{price:.2f}",
                            "Стоимость": f"{total_value:.2f}"
                        })

                    if positions_data:
                        df = pd.DataFrame(positions_data)
                        st.subheader("Открытые позиции (включая Фьючерсы)")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("Портфель пуст или позиции отсутствуют.")

        except Exception as e:
            st.error(f"Ошибка при получении данных от брокера: {e}")

elif password != "":
    st.error("Неверный пароль")
