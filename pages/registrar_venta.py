# pages/registrar_venta.py

import streamlit as st
import pandas as pd
from datetime import datetime
import requests

from services.ui_helpers import require_login, logout_button, sidebar_menu

from data.ventas_queries import (
    get_productos_con_stock,
    get_empleados_activos,
    registrar_venta_completa,
)

st.set_page_config(page_title="Registrar Venta - Senda Café", layout="wide")


def trigger_stock_alert_lambda() -> tuple[bool, str]:
    """
    Dispara la Lambda (Function URL) para evaluar stock crítico y enviar emails.
    No debe romper el flujo de ventas: si falla, devolvemos ok=False y el error.
    """
    url = st.secrets.get("ALERTS_API_URL", "").strip()
    api_key = st.secrets.get("API_KEY", "").strip()

    if not url or not api_key:
        return False, "Faltan ALERTS_API_URL o API_KEY en Streamlit Secrets."

    # Normalizar: evitar dobles // al hacer POST
    if not url.endswith("/"):
        url = url + "/"

    try:
        resp = requests.post(
            url,
            headers={"x-api-key": api_key},
            json={"source": "streamlit_sale", "ts": datetime.utcnow().isoformat()},
            timeout=10,
        )
        if resp.status_code != 200:
            return False, f"Lambda status={resp.status_code} body={resp.text[:500]}"
        return True, resp.text
    except Exception as e:
        return False, str(e)


def main():
    # 🧭 Menú lateral
    sidebar_menu()

    # 🔐 Permitir admin + dueños
    require_login(roles=["admin", "owner"])

    st.title("🧾 Registrar Venta")

    # Mostrar usuario logueado
    user = st.session_state["user"]
    st.caption(f"Usuario: {user['nombre']} | Rol: {user['rol']}")
    logout_button()

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
            options=df_emp["id_empleado"].tolist(),
            format_func=lambda x: df_emp.set_index("id_empleado").loc[x, "nombre"],
        )

    with col2:
        servicio = st.selectbox("Servicio", options=["SALÓN", "TAKE AWAY", "DELIVERY"])

    with col3:
        metodo_pago = st.selectbox("Método de pago", options=["EFECTIVO", "DÉBITO", "CRÉDITO", "QR", "OTRO"])

    fecha_hora = datetime.now()

    st.markdown("---")
    st.subheader("🧺 Detalle del ticket")

    # Inicializar carrito
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
                options=df_prod["id_producto"].tolist(),
                format_func=lambda x: df_prod.set_index("id_producto").loc[x, "nombre"],
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
                step=1,
            )

        with c3:
            precio_unitario = st.number_input(
                "Precio unitario",
                min_value=0.0,
                value=precio_sugerido,
                step=100.0,
            )

        with c4:
            st.write(f"Stock disp.: {stock_disp}")

        agregar = st.form_submit_button("➕ Agregar al ticket")

        if agregar:
            if stock_disp <= 0:
                st.error("No hay stock disponible de este producto.")
            elif int(cantidad) > stock_disp:
                st.error("La cantidad supera el stock disponible.")
            else:
                st.session_state["carrito"].append(
                    {
                        "id_producto": int(id_prod_sel),
                        "producto": str(prod_row["nombre"]),
                        "cantidad": int(cantidad),
                        "precio_unitario": float(precio_unitario),
                    }
                )
                st.success("Producto agregado al ticket.")

    # ======================
    # Mostrar carrito
    # ======================
    carrito = st.session_state["carrito"]

    if not carrito:
        st.info("No hay productos en el ticket todavía.")
        return

    df_cart = pd.DataFrame(carrito)
    df_cart["subtotal"] = df_cart["cantidad"] * df_cart["precio_unitario"]
    total = float(df_cart["subtotal"].sum())

    st.table(df_cart[["producto", "cantidad", "precio_unitario", "subtotal"]])
    st.markdown(f"### 💰 Total del ticket: ${total:,.2f}")

    c1, c2, _ = st.columns([1, 1, 3])

    with c1:
        confirmar = st.button("✅ Confirmar venta")

    with c2:
        cancelar = st.button("🗑️ Vaciar ticket")

    if cancelar:
        st.session_state["carrito"] = []
        st.success("Ticket vaciado.")
        return

    if confirmar:
        try:
            items = [
                {
                    "id_producto": int(row["id_producto"]),
                    "cantidad": int(row["cantidad"]),
                    "precio_unitario": float(row["precio_unitario"]),
                }
                for _, row in df_cart.iterrows()
            ]

            # 1) Registrar venta en DB
            id_venta, total_ticket = registrar_venta_completa(
                fecha_hora=fecha_hora,
                servicio=servicio,
                id_empleado=int(empleado_sel),
                metodo_pago=metodo_pago,
                items=items,
                id_usuario=int(user["id_usuario"]),
                ticket_id_origen=None,
            )

            # 2) Disparar Lambda (no rompe si falla)
            ok, msg = trigger_stock_alert_lambda()
            if not ok:
                st.warning(f"Venta OK (ID: {id_venta}) pero alerta de stock no se pudo ejecutar: {msg}")
            else:
                # opcional: si querés ver el JSON de respuesta:
                # st.code(msg, language="json")
                pass

            st.success(f"Venta registrada correctamente (ID: {id_venta}) – Total: ${float(total_ticket):,.2f}")
            st.session_state["carrito"] = []

        except Exception as e:
            st.error(f"Error al registrar la venta: {e}")


if __name__ == "__main__":
    main()
