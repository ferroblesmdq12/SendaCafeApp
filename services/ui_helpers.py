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