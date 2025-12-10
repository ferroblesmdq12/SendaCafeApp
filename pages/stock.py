# pages/stock.py

import streamlit as st
import pandas as pd

from services.ui_helpers import require_login, logout_button, sidebar_menu

from data.ventas_queries import (
    get_stock_resumen,
    get_productos_con_stock,
    registrar_entrada_stock,
)

st.set_page_config(page_title="Gestión de Stock - Senda Café", layout="wide")

def main():

    # 🧭 Menú lateral
    sidebar_menu()
    
    # 🔐 Solo admin + owner puede gestionar stock
    require_login(roles=["admin", "owner"])

    st.title("📦 Gestión de Stock")

    user = st.session_state["user"]
    st.caption(f"Usuario: {user['nombre']} | Rol: {user['rol']}")
    logout_button()

    st.subheader("📊 Stock actual por producto")

    df_stock = get_stock_resumen()
    if df_stock.empty:
        st.info("No hay datos de stock.")
    else:
        st.dataframe(df_stock)

    st.markdown("---")
    st.subheader("➕ Registrar entrada de mercadería")

    df_prod = get_productos_con_stock()
    if df_prod.empty:
        st.info("No hay productos cargados.")
        st.stop()

    col1, col2, col3 = st.columns(3)

    with col1:
        id_prod = st.selectbox(
            "Producto",
            options=df_prod["id_producto"],
            format_func=lambda x: df_prod.set_index("id_producto").loc[x, "nombre"]
        )

    with col2:
        cantidad = st.number_input("Cantidad a ingresar", min_value=1, value=10, step=1)

    with col3:
        comentario = st.text_input("Comentario (opcional)", value="Compra de mercadería")

    if st.button("💾 Registrar entrada"):
        try:
            registrar_entrada_stock(
                id_producto=id_prod,
                cantidad=int(cantidad),
                comentario=comentario,
                id_usuario=user["id_usuario"]  # <--- AHORA USAMOS EL USUARIO LOGUEADO
            )
            st.success("Entrada de stock registrada correctamente.")
        except Exception as e:
            st.error(f"Error al registrar entrada de stock: {e}")


if __name__ == "__main__":
    main()


# Con esto puedo ver:

# Ver stock actual.

# Cargar mercadería.

# Registrar automáticamente movimiento de stock.