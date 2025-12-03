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
