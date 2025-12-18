import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

from core.db import get_conn, init_db, seed_if_empty
from core.ef371 import load_ef_table
from core.calc import calculate_co2


st.set_page_config(page_title="Админ-панель", layout="wide")
init_db()
seed_if_empty()

user = st.session_state.get("user")
if not user:
    st.error("Нужно войти в систему (страница «Вход»).")
    st.stop()
if user["role"] != "admin":
    st.warning("Эта страница для роли admin. Перейдите в «Кабинет филиала».")
    st.stop()

st.title("Администратор: консолидация + расчет CO₂ по МПР 371")

df_ef = load_ef_table()

conn = get_conn()
branches = pd.read_sql_query("SELECT branch_id, branch_name FROM branches ORDER BY branch_name", conn)
conn.close()

# Filters
with st.expander("Фильтры", expanded=True):
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        branch_opt = st.selectbox(
            "Филиал",
            options=["Все"] + branches["branch_name"].tolist()
        )
    with c2:
        date_from = st.date_input("Дата от", value=date.today().replace(day=1))
        date_to = st.date_input("Дата до", value=date.today())
    with c3:
        fuel_filter = st.text_input("Фильтр по топливу (подстрока)", value="")

# Load data
conn = get_conn()
df = pd.read_sql_query(
    """SELECT fu.usage_id, fu.created_at, b.branch_name, fu.username, fu.fuel_name, fu.qty, fu.unit, fu.comment
         FROM fuel_usage fu
         JOIN branches b ON b.branch_id = fu.branch_id
         ORDER BY fu.created_at DESC""",
    conn
)
conn.close()

if df.empty:
    st.info("Пока нет данных от филиалов.")
    st.stop()

df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
mask = (df["created_at"].dt.date >= date_from) & (df["created_at"].dt.date <= date_to)
if branch_opt != "Все":
    mask &= (df["branch_name"] == branch_opt)
if fuel_filter.strip():
    mask &= df["fuel_name"].str.contains(fuel_filter.strip(), case=False, na=False)

df_f = df.loc[mask].copy()

if df_f.empty:
    st.info("По выбранным фильтрам данных нет. Измени период/филиал или дождись ввода филиалов.")
    st.stop()

st.subheader("Сырые данные (после фильтров)")
st.dataframe(df_f, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Расчет выбросов CO₂ (Q × НТС × EF_CO2)")
df_calc = calculate_co2(df_f, df_ef)

# Highlight issues
issues = df_calc[df_calc["LHV"].isna() | df_calc["EF_CO2"].isna() | (~df_calc["unit_match"])]
if not issues.empty:
    st.warning("Есть строки с проблемами справочника/единиц. Проверь топливо, НТС/EF или единицы измерения.")
    st.dataframe(
        issues[["usage_id", "created_at", "branch_name", "fuel_name", "qty", "unit", "unit_ef", "LHV", "EF_CO2", "unit_match"]],
        use_container_width=True,
        hide_index=True
    )

# Main result table
show_cols = ["created_at", "branch_name", "username", "fuel_name", "qty", "unit", "LHV", "EF_CO2", "CO2_kg", "CO2_t", "comment"]
st.dataframe(df_calc[show_cols], use_container_width=True, hide_index=True)

# Aggregations
st.subheader("Итоги")
c1, c2, c3 = st.columns(3)

total_t = float(pd.to_numeric(df_calc["CO2_t"], errors="coerce").fillna(0).sum())
with c1:
    st.metric("Итого CO₂, т", f"{total_t:,.3f}".replace(",", " "))

by_branch = (df_calc.groupby("branch_name", dropna=False)["CO2_t"]
             .sum().reset_index().sort_values("CO2_t", ascending=False))
with c2:
    st.write("По филиалам (т CO₂)")
    st.dataframe(by_branch, use_container_width=True, hide_index=True)

by_fuel = (df_calc.groupby("fuel_name", dropna=False)["CO2_t"]
           .sum().reset_index().sort_values("CO2_t", ascending=False))
with c3:
    st.write("По топливу (т CO₂)")
    st.dataframe(by_fuel, use_container_width=True, hide_index=True)

st.divider()

# Export
st.subheader("Экспорт")
export_df = df_calc[show_cols].copy()

csv_bytes = export_df.to_csv(index=False).encode("utf-8-sig")
st.download_button("Скачать CSV", data=csv_bytes, file_name="mpr371_emissions.csv", mime="text/csv")

# XLSX
out = BytesIO()
with pd.ExcelWriter(out, engine="openpyxl") as writer:
    export_df.to_excel(writer, index=False, sheet_name="Data")
    by_branch.to_excel(writer, index=False, sheet_name="ByBranch")
    by_fuel.to_excel(writer, index=False, sheet_name="ByFuel")
st.download_button("Скачать XLSX", data=out.getvalue(), file_name="mpr371_emissions.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.caption("Примечание: справочник МПР 371 в демо — укороченный. Замени app/data/tblEF_371.csv на полный.")
