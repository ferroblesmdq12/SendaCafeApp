# services/ui_helpers.py

import streamlit as st
import base64


def convert_image_to_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


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

    logo_path = "assets/images/Logo_cafe.png"

    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{convert_image_to_base64(logo_path)}" width="120">
        </div>
        """,
        unsafe_allow_html=True
    )


###################################################
# LOGIN
###################################################

def require_login(roles=None):
    """
    Protege páginas según sesión y rol.
    roles = lista de roles permitidos, ej: ["admin", "owner", "viewer"]
    """
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.error("❌ Debes iniciar sesión para continuar.")
        st.stop()

    if roles is not None:
        rol_usuario = st.session_state["user"].get("rol")

        if rol_usuario not in roles:
            st.error("⛔ No tenés permisos para ver esta sección.")
            st.stop()


def logout_button():
    """
    Muestra botón para cerrar sesión.
    """
    if st.button("Cerrar sesión"):
        st.session_state["user"] = None
        st.rerun()


###################################################
# BARRA LATERAL
###################################################

def safe_page_link(page: str, label: str):
    """
    Envuelve st.page_link en un try/except para evitar errores
    si una página no existe o el nombre es incorrecto.
    """
    try:
        st.page_link(page, label=label)
    except Exception:
        pass


def hide_streamlit_default_nav():
    """
    Oculta el navegador de páginas nativo de Streamlit.
    """
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def sidebar_menu():
    """
    Menú lateral reutilizable para toda la app.
    Muestra opciones según si hay usuario logueado y su rol.

    Roles:
    - admin: ve todo
    - owner: ve todo
    - viewer: solo lectura / gráficos
    """

    hide_streamlit_default_nav()

    user = st.session_state.get("user")

    with st.sidebar:
        st.image("assets/images/Logo_cafe.png", width=140)
        st.markdown("### Menú")

        # Siempre visible
        safe_page_link("app.py", label="🏠 Inicio")

        if user is None:
            safe_page_link("pages/login.py", label="🔐 Iniciar sesión")

        else:
            rol = user.get("rol")

            # Páginas de solo lectura / análisis
            safe_page_link("pages/dashboard.py", label="📊 Dashboard general")
            safe_page_link("pages/ventas.py", label="📈 Ventas")
            safe_page_link("pages/empleados.py", label="🧑‍🍳 Empleados")
            safe_page_link("pages/ganancias.py", label="💰 Ganancias")

            # Páginas de escritura/modificación
            # Solo admin y owner pueden registrar ventas o modificar stock
            if rol in ["admin", "owner"]:
                safe_page_link("pages/registrar_venta.py", label="🧾 Registrar venta")
                safe_page_link("pages/stock.py", label="📦 Gestión de stock")

        st.markdown("---")

        if user is not None:
            st.caption(f"👤 {user['nombre']} ({user['rol']})")