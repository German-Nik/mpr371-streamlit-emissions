import streamlit as st
from core.db import init_db, seed_if_empty
from core.auth import get_branch_name

st.set_page_config(page_title="МПР 371 — учет топлива и выбросов", layout="wide")

init_db()
seed_if_empty()

st.title("Расчет выбросов ПГ (по МПР 371)")

user = st.session_state.get("user")

col1, col2 = st.columns([2,1], vertical_alignment="top")

with col1:
    st.markdown("""
**Что умеет приложение**
- Вход в систему (роль **user** / **admin**)
- Филиал (user) вносит расход топлива (вид топлива из справочника 371)
- Админ видит общую таблицу, фильтрует и считает CO₂ по формуле: **Q × НТС × EF_CO2**
- Экспорт итоговой таблицы в CSV/XLSX

**Демо-учетки**
- admin / adminpass (администратор)
- user1 / userpass (филиал Котлас)
- user2 / userpass (филиал Архангельск)
""")

with col2:
    st.subheader("Статус сессии")
    if user:
        branch = get_branch_name(user.get("branch_id"))
        st.success(f"Вы вошли как: {user['username']} ({user['role']})")
        if branch:
            st.info(f"Филиал: {branch}")
        if st.button("Выйти"):
            st.session_state.pop("user", None)
            st.rerun()
    else:
        st.warning("Вы не вошли. Перейдите на страницу **Вход** слева.")

st.divider()
st.caption("Навигация: слева в меню Pages → Вход → Кабинет филиала / Админ-панель (зависит от роли).")



