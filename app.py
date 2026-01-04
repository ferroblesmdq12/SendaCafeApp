# app.py

import streamlit as st
from services.ui_helpers import logout_button, sidebar_menu

st.set_page_config(page_title="Senda Café", layout="wide")

st.image("assets/images/Logo_cafe.png", width=120)
st.title("☕ Bienvenido a Senda Café")

def main():

    # ⬅️ Menú lateral siempre visible
    sidebar_menu()

    # st.image("assets/images/Logo_cafe.png", width=120)
    # st.title("☕ Bienvenido a Senda Café")

    # Si NO está logueado → enviarlo a Login
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.info("Para continuar, iniciá sesión desde el menú de la izquierda.")
        st.page_link("pages/login.py", label="🔐 Ir a iniciar sesión")
        return

    # Si SÍ está logueado
    user = st.session_state["user"]
    st.success(f"Hola {user['nombre']} 👋 – Bienvenido nuevamente.")

    logout_button()

    st.markdown("---")
    st.write("👉 Usá el menú de la izquierda para acceder al dashboard, registrar ventas o gestionar stock.")

import streamlit as st
from services.alerts import send_stock_critical_email

st.divider()
st.subheader("Test Alert Email (solo debug)")

if st.button("TEST SENDGRID"):
    send_stock_critical_email("TEST SENDGRID", 1, 10)
    st.success("Se ejecutó el envío (revisar email y Logs).")

sg = SendGridAPIClient(api_key)
try:
    resp = sg.send(message)
    print("SENDGRID_STATUS:", resp.status_code)
    print("SENDGRID_BODY:", resp.body)
except Exception as e:
    # Intenta extraer información útil si viene del cliente de SendGrid
    status = getattr(e, "status_code", None)
    body = getattr(e, "body", None)
    headers = getattr(e, "headers", None)

    print("SENDGRID_EXCEPTION:", repr(e))
    print("SENDGRID_EXCEPTION_STATUS:", status)
    print("SENDGRID_EXCEPTION_BODY:", body)
    print("SENDGRID_EXCEPTION_HEADERS:", headers)

    raise RuntimeError(f"SendGrid error al enviar alerta: {repr(e)}")



if __name__ == "__main__":
    main()
