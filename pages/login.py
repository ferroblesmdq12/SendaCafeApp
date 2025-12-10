# pages/0_Login.py

import streamlit as st
from data.usuarios_queries import authenticate
from services.ui_helpers import logout_button,sidebar_menu

def main():

    # 🧭 Menú lateral
    sidebar_menu()

    st.title("🔐 Iniciar sesión - Senda Café")

    # Si ya está logueado, muestro info y botón de logout
    if "user" in st.session_state and st.session_state["user"] is not None:
        user = st.session_state["user"]
        st.success(f"Ya estás logueado como {user['nombre']} ({user['rol']})")
        logout_button()
        return

    with st.form("login_form"):
        identifier = st.text_input("Email o usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")

    if submit:
        user = authenticate(identifier, password)
        if user:
            st.session_state["user"] = user
            st.success(f"Bienvenido, {user['nombre']} 👋")
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas o usuario inactivo.")

if __name__ == "__main__":
    main()
