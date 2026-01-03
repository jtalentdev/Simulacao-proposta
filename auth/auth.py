import streamlit as st
import hashlib

# ================= USUÁRIOS =================
# Formato:
# "usuario": "hash_sha256_da_senha"
USERS = {
    "jtalentdev": "681fae29b727e172cd8605c3444ec059c2340c9ae5941a9e9ecc46c0081db7c8"
}

# ================= FUNÇÕES =================

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def login():
    # Evita redesenhar a tela de login se já estiver autenticado
    if st.session_state.get("logged", False):
        return

    st.title("🔐 Login")

    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in USERS and USERS[user] == _hash(password):
            st.session_state["logged"] = True
            st.session_state["user"] = user
            st.success("Login realizado com sucesso")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")
