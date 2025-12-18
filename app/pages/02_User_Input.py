import streamlit as st
import pandas as pd
from datetime import datetime, date
from core.db import get_conn, init_db, seed_if_empty
from core.ef371 import load_ef_table, list_fuels, get_unit_for_fuel

st.set_page_config(page_title="Кабинет филиала", layout="wide")
init_db()
seed_if_empty()

user = st.session_state.get("user")
if not user:
    st.error("Нужно войти в систему (страница «Вход»).")
    st.stop()
if user["role"] != "user":
    st.warning("Эта страница для роли user. Перейдите в «Админ-панель».")
    st.stop()

df_ef = load_ef_table()
fuels = list_fuels(df_ef)

st.title("Кабинет филиала: ввод расхода топлива")
st.caption("Данные видны администратору, расчет CO₂ делается в админ-панели.")

# form
with st.form("usage_form"):
    fuel = st.selectbox("Вид топлива (МПР 371)", options=fuels)
    unit = get_unit_for_fuel(df_ef, fuel)
    qty = st.number_input(f"Количество, {unit}", min_value=0.0, value=0.0, step=1.0)
    comment = st.text_input("Комментарий (опционально)")
    submitted = st.form_submit_button("Сохранить запись")

if submitted:
    if qty <= 0:
        st.error("Количество должно быть > 0.")
    else:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO fuel_usage(created_at, branch_id, username, fuel_name, qty, unit, comment)
                   VALUES (?,?,?,?,?,?,?)""",
            (datetime.utcnow().isoformat(timespec="seconds"), user["branch_id"], user["username"], fuel, float(qty), unit, comment)
        )
        conn.commit()
        conn.close()
        st.success("Запись сохранена.")
        st.rerun()

st.divider()

# view own records with date filter
st.subheader("Мои записи")
col1, col2 = st.columns(2)
with col1:
    date_from = st.date_input("Дата от", value=date.today().replace(day=1))
with col2:
    date_to = st.date_input("Дата до", value=date.today())

conn = get_conn()
df = pd.read_sql_query(
    """SELECT created_at, fuel_name, qty, unit, comment
         FROM fuel_usage
         WHERE branch_id = ?
         ORDER BY created_at DESC""",
    conn,
    params=(user["branch_id"],)
)
conn.close()

if df.empty:
    st.info("Пока нет записей.")
    st.stop()

df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
mask = (df["created_at"].dt.date >= date_from) & (df["created_at"].dt.date <= date_to)
df = df.loc[mask].copy()

st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("Подсказка: если нужно редактирование/удаление — добавим кнопки и строгие права доступа.")
