# app.py

import streamlit as st
from services.ui_helpers import logout_button

st.set_page_config(page_title="Senda Café", layout="wide")

st.image("assets/images/Logo_cafe.png", width=120)
st.title("☕ Bienvenido a Senda Café")

def main():

    # Si NO está logueado → enviarlo a Login
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.info("Para continuar, iniciá sesión desde el menú de la izquierda.")
        st.page_link("pages/0_Login.py", label="🔐 Ir a iniciar sesión")
        return

    # Si SÍ está logueado
    user = st.session_state["user"]
    st.success(f"Hola {user['nombre']} 👋 – Bienvenido nuevamente.")

    logout_button()

    st.markdown("---")
    st.write("👉 Usá el menú de la izquierda para acceder al dashboard, registrar ventas o gestionar stock.")

if __name__ == "__main__":
    main()
