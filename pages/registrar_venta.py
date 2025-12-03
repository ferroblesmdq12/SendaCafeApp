from services.ui_helpers import mostrar_logo
import streamlit as st
import pandas as pd
from datetime import datetime



from data.ventas_queries import (
    get_productos_con_stock,
    get_empleados_activos,
    registrar_venta_completa,
)

st.set_page_config(page_title="Registrar Venta - Senda Café", layout="wide")

st.title("🧾 Registrar Venta")

# ======================
# Cargar datos base
# ======================
df_prod = get_productos_con_stock()
df_emp = get_empleados_activos()

if df_prod.empty:
    st.error("No hay productos con stock cargados.")
    st.stop()

if df_emp.empty:
    st.error("No hay empleados activos.")
    st.stop()

# ======================
# Datos generales venta
# ======================
col1, col2, col3 = st.columns(3)

with col1:
    empleado_sel = st.selectbox(
        "Empleado",
        options=df_emp["id_empleado"],
        format_func=lambda x: df_emp.set_index("id_empleado").loc[x, "nombre"]
    )

with col2:
    servicio = st.selectbox(
        "Servicio",
        options=["SALÓN", "TAKE AWAY", "DELIVERY"]
    )

with col3:
    metodo_pago = st.selectbox(
        "Método de pago",
        options=["EFECTIVO", "DÉBITO", "CRÉDITO", "QR", "OTRO"]
    )

fecha_hora = datetime.now()

st.markdown("---")
st.subheader("🧺 Detalle del ticket")

# Inicializar carrito en session_state
if "carrito" not in st.session_state:
    st.session_state["carrito"] = []

# ======================
# Form para agregar ítems
# ======================
with st.form("form_item"):
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])

    with c1:
        id_prod_sel = st.selectbox(
            "Producto",
            options=df_prod["id_producto"],
            format_func=lambda x: df_prod.set_index("id_producto").loc[x, "nombre"]
        )

    prod_row = df_prod.set_index("id_producto").loc[id_prod_sel]
    stock_disp = int(prod_row["stock_actual"])
    precio_sugerido = float(prod_row["precio_venta"])

    with c2:
        cantidad = st.number_input(
            "Cantidad",
            min_value=1,
            max_value=max(stock_disp, 1),
            value=1,
            step=1
        )

    with c3:
        precio_unitario = st.number_input(
            "Precio unitario",
            min_value=0.0,
            value=precio_sugerido,
            step=100.0
        )

    with c4:
        st.write(f"Stock disp.: {stock_disp}")

    agregar = st.form_submit_button("➕ Agregar al ticket")

    if agregar:
        if stock_disp <= 0:
            st.error("No hay stock disponible de este producto.")
        elif cantidad > stock_disp:
            st.error("La cantidad supera el stock disponible.")
        else:
            st.session_state["carrito"].append({
                "id_producto": id_prod_sel,
                "producto": prod_row["nombre"],
                "cantidad": int(cantidad),
                "precio_unitario": float(precio_unitario)
            })
            st.success("Producto agregado al ticket.")

# ======================
# Mostrar carrito
# ======================
carrito = st.session_state["carrito"]

if not carrito:
    st.info("No hay productos en el ticket todavía.")
else:
    df_cart = pd.DataFrame(carrito)
    df_cart["subtotal"] = df_cart["cantidad"] * df_cart["precio_unitario"]
    total = df_cart["subtotal"].sum()

    st.table(df_cart[["producto", "cantidad", "precio_unitario", "subtotal"]])
    st.markdown(f"### 💰 Total del ticket: ${total:,.2f}")

    c1, c2, c3 = st.columns([1, 1, 3])

    with c1:
        confirmar = st.button("✅ Confirmar venta")

    with c2:
        cancelar = st.button("🗑️ Vaciar ticket")

    if cancelar:
        st.session_state["carrito"] = []
        st.success("Ticket vaciado.")

    if confirmar:
        try:
            items = [
                {
                    "id_producto": row["id_producto"],
                    "cantidad": row["cantidad"],
                    "precio_unitario": row["precio_unitario"],
                }
                for _, row in df_cart.iterrows()
            ]

            # Por ahora id_usuario=None (luego lo llenamos con el login real)
            id_venta, total_ticket = registrar_venta_completa(
                fecha_hora=fecha_hora,
                servicio=servicio,
                id_empleado=empleado_sel,
                metodo_pago=metodo_pago,
                items=items,
                id_usuario=None,
                ticket_id_origen=None,
            )

            st.success(f"Venta registrada correctamente (ID: {id_venta}) - Total: ${total_ticket:,.2f}")
            st.session_state["carrito"] = []

        except Exception as e:
            st.error(f"Error al registrar la venta: {e}")


# Cada venta:

# Se guarda en ventas

# Sus detalles en ventas_detalle

# Baja stock en stock

# Crea movimientos en movimientos_stock

# Y tu dashboard va a ver esas ventas automáticamente.