# app.py

# import streamlit as st
# from services.ui_helpers import logout_button, sidebar_menu

# st.set_page_config(page_title="Senda Café", layout="wide")

# st.image("assets/images/Logo_cafe.png", width=120)
# st.title("☕ Bienvenido a Senda Café")

# def main():

#     # ⬅️ Menú lateral siempre visible
#     sidebar_menu()

#     # st.image("assets/images/Logo_cafe.png", width=120)
#     # st.title("☕ Bienvenido a Senda Café")

#     # Si NO está logueado → enviarlo a Login
#     if "user" not in st.session_state or st.session_state["user"] is None:
#         st.info("Para continuar, iniciá sesión desde el menú de la izquierda.")
#         st.page_link("pages/login.py", label="🔐 Ir a iniciar sesión")
#         return

#     # Si SÍ está logueado
#     user = st.session_state["user"]
#     st.success(f"Hola {user['nombre']} 👋 – Bienvenido nuevamente.")

#     logout_button()

#     st.markdown("---")
#     st.write("👉 Usá el menú de la izquierda para acceder al dashboard, registrar ventas o gestionar stock.")


# if __name__ == "__main__":
#     main()


import streamlit as st
from services.ui_helpers import logout_button, sidebar_menu
from services.alerts import send_stock_critical_email
from core.config import get_env_var

st.set_page_config(page_title="Senda Café", layout="wide")

def main():
    sidebar_menu()

    st.image("assets/images/Logo_cafe.png", width=120)
    st.title("☕ Bienvenido a Senda Café")

    st.divider()
    st.subheader("🧪 Test SendGrid (debug)")

    if st.button("TEST SENDGRID"):
        # ---- DEBUG: verificar qué key está leyendo Streamlit ----
        k = get_env_var("SENDGRID_API_KEY") or ""
        st.write("SENDGRID_API_KEY prefix:", k[:3], "len:", len(k))

        try:
            send_stock_critical_email("TEST SENDGRID", 1, 10)
            st.success("Test disparado. Revisá email y Logs.")
        except Exception as e:
            st.error("Falló el envío. Revisá los Logs en Streamlit Cloud.")
            st.write(str(e))

    # resto de tu lógica normal
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.info("Para continuar, iniciá sesión desde el menú.")
        st.page_link("pages/login.py", label="🔐 Ir a iniciar sesión")
        return

    user = st.session_state["user"]
    st.success(f"Hola {user['nombre']} 👋")
    logout_button()

if __name__ == "__main__":
    main()
