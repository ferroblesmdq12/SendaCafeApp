
#ui_helpers.py
import streamlit as st

def mostrar_logo():
    """
    Muestra el logo de Senda Café centrado arriba de la página.
    """
    st.markdown(
        """
        <style>
            .logo-container {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    logo_path = "assets/images/Logo_café.png"

    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{convert_image_to_base64(logo_path)}" width="120">
        </div>
        """,
        unsafe_allow_html=True
    )


import base64

def convert_image_to_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


###################################################
#
# LOGIN
#
###################################################


def require_login(roles=None):
    """
    Usar al comienzo de cada página que quieras proteger.
    roles = lista de roles permitidos, ej: ["admin", "owner"]
    """
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.error("❌ Debes iniciar sesión para continuar.")
        st.stop()

    if roles is not None:
        rol_usuario = st.session_state["user"]["rol"]
        if rol_usuario not in roles:
            st.error("⛔ No tenés permisos para ver esta sección.")
            st.stop()


def logout_button():
    """
    Muestra botón para cerrar sesión.
    """
    if st.button("Cerrar sesión"):
        st.session_state["user"] = None
        st.experimental_rerun()


#################
#
# Barra Lateral
#
########

# services/ui_helpers.py
import streamlit as st



def sidebar_menu():
    """
    Menú lateral común para toda la app.
    """
    with st.sidebar:
        # Logo arriba
        st.image("assets/images/Logo_cafe.png", width=120)
        st.markdown("### Menú")

        # Links a las páginas principales
        st.page_link("app.py", label="🏠 Inicio")
        st.page_link("pages/0_Login.py", label="🔐 Iniciar sesión")
        st.page_link("pages/dashboard.py", label="📊 Dashboard general")
        st.page_link("pages/registrar_venta.py", label="🧾 Registrar venta")
        st.page_link("pages/stock.py", label="📦 Gestión de stock")
        # Más adelante acá vamos a agregar:
        # st.page_link("pages/dashboard_empleados.py", label="🧑‍🍳 Empleados y horarios")
