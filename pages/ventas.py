#pages/ventas.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

from services.ui_helpers import require_login, logout_button, sidebar_menu
from data.ventas_queries import (
    get_empleados_activos,
    get_catalogo_productos_activos,
    get_ventas_resumen_filtrado,
    get_tickets_filtrados,
    get_top_productos_filtrado,
    get_top_empleados_filtrado,
)

st.set_page_config(page_title="Ventas - Senda Café", layout="wide")

def main():
    sidebar_menu()
    require_login(roles=["admin", "owner"])

    st.title("📈 Ventas")
    logout_button()

    # -------------------------
    # Filtros
    # -------------------------
    today = date.today()
    default_from = today - timedelta(days=30)

    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        date_from = st.date_input("Desde", value=default_from)
    with f2:
        date_to = st.date_input("Hasta", value=today)

    df_emp = get_empleados_activos()
    df_prod = get_catalogo_productos_activos()

    with f3:
        empleados_sel = st.multiselect(
            "Empleado(s)",
            options=df_emp["id_empleado"].tolist() if not df_emp.empty else [],
            format_func=lambda x: df_emp.set_index("id_empleado").loc[x, "nombre"] if not df_emp.empty else str(x),
        )

    productos_sel = st.multiselect(
        "Producto(s)",
        options=df_prod["id_producto"].tolist() if not df_prod.empty else [],
        format_func=lambda x: df_prod.set_index("id_producto").loc[x, "nombre"] if not df_prod.empty else str(x),
    )

    if date_from > date_to:
        st.error("Rango inválido: 'Desde' no puede ser mayor que 'Hasta'.")
        st.stop()

    # -------------------------
    # Data
    # -------------------------
    df_res = get_ventas_resumen_filtrado(date_from, date_to, empleados_sel, productos_sel)
    df_tickets = get_tickets_filtrados(date_from, date_to, empleados_sel, productos_sel)
    df_top_prod = get_top_productos_filtrado(date_from, date_to, empleados_sel, productos_sel)
    df_top_emp = get_top_empleados_filtrado(date_from, date_to, empleados_sel, productos_sel)

    # -------------------------
    # KPIs
    # -------------------------
    total_ventas = float(df_res["ventas_total"].sum()) if not df_res.empty else 0.0
    tickets = int(df_res["tickets"].sum()) if not df_res.empty else 0
    ticket_prom = (total_ventas / tickets) if tickets else 0.0

    k1, k2, k3 = st.columns(3)
    k1.metric("Ventas totales", f"${total_ventas:,.0f}")
    k2.metric("Tickets", f"{tickets:,}")
    k3.metric("Ticket promedio", f"${ticket_prom:,.0f}")

    st.divider()

    # -------------------------
    # Gráficos
    # -------------------------
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📆 Ventas por día")
        if df_res.empty:
            st.info("No hay ventas para los filtros seleccionados.")
        else:
            fig = px.line(df_res, x="dia", y="ventas_total", markers=True)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🏆 Top productos")
        if df_top_prod.empty:
            st.info("Sin datos para top productos.")
        else:
            fig = px.bar(df_top_prod, x="producto", y="unidades")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("👥 Top empleados")
    if df_top_emp.empty:
        st.info("Sin datos para top empleados.")
    else:
        fig = px.bar(df_top_emp, x="empleado", y="total")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------------------------
    # Tabla de tickets
    # -------------------------
    st.subheader("🧾 Tickets filtrados")
    if df_tickets.empty:
        st.info("No hay tickets para los filtros seleccionados.")
    else:
        st.dataframe(df_tickets, use_container_width=True)
        st.download_button(
            "⬇️ Descargar (CSV)",
            data=df_tickets.to_csv(index=False).encode("utf-8"),
            file_name="tickets_filtrados.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()


