import streamlit as st
from core.auth import authenticate, get_branch_name
from core.db import init_db, seed_if_empty

st.set_page_config(page_title="Вход", layout="centered")
init_db()
seed_if_empty()

st.title("Вход")

if st.session_state.get("user"):
    u = st.session_state["user"]
    branch = get_branch_name(u.get("branch_id"))
    st.success(f"Уже вошли как: {u['username']} ({u['role']})" + (f", {branch}" if branch else ""))
    if st.button("Выйти"):
        st.session_state.pop("user", None)
        st.rerun()
    st.stop()

with st.form("login_form"):
    username = st.text_input("Логин", value="")
    password = st.text_input("Пароль", value="", type="password")
    submitted = st.form_submit_button("Войти")

if submitted:
    user = authenticate(username.strip(), password)
    if not user:
        st.error("Неверный логин или пароль.")
    else:
        st.session_state["user"] = user
        st.success("Вход выполнен.")
        st.rerun()

st.info("Демо: admin/adminpass, user1/userpass, user2/userpass")
