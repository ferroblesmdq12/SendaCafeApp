import streamlit as st
import plotly.express as px
from datetime import date, timedelta

from services.ui_helpers import require_login, logout_button, sidebar_menu
from data.ventas_queries import (
    get_empleados_activos,
    get_catalogo_productos_activos,
    get_empleados_ranking_filtrado,
    get_empleado_resumen_filtrado,
    get_empleado_ventas_por_dia,
    get_empleado_top_productos,
)

st.set_page_config(page_title="Empleados - Senda Café", layout="wide")

def main():
    sidebar_menu()
    require_login(roles=["admin", "owner"])

    st.title("🧑‍🍳 Empleados")
    logout_button()

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
        productos_sel = st.multiselect(
            "Producto(s) (opcional)",
            options=df_prod["id_producto"].tolist() if not df_prod.empty else [],
            format_func=lambda x: df_prod.set_index("id_producto").loc[x, "nombre"] if not df_prod.empty else str(x),
        )

    if date_from > date_to:
        st.error("Rango inválido: 'Desde' no puede ser mayor que 'Hasta'.")
        st.stop()

    st.divider()

    # Ranking general
    st.subheader("🏁 Ranking de empleados (período seleccionado)")
    df_rank = get_empleados_ranking_filtrado(date_from, date_to, productos=productos_sel, limit=20)

    if df_rank.empty:
        st.info("No hay datos para el período/filtros seleccionados.")
        return

    c1, c2 = st.columns([2, 1])
    with c1:
        st.dataframe(df_rank, use_container_width=True)
    with c2:
        fig = px.bar(df_rank.head(10), x="empleado", y="ventas_total")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Detalle por empleado
    st.subheader("🔎 Detalle por empleado")
    emp_options = df_emp["id_empleado"].tolist() if not df_emp.empty else df_rank["id_empleado"].dropna().tolist()

    id_emp = st.selectbox(
        "Seleccionar empleado",
        options=emp_options,
        format_func=lambda x: df_emp.set_index("id_empleado").loc[x, "nombre"] if not df_emp.empty else str(x),
    )

    df_kpi = get_empleado_resumen_filtrado(date_from, date_to, id_empleado=id_emp, productos=productos_sel)

    ventas_total = float(df_kpi["ventas_total"].iloc[0])
    tickets = int(df_kpi["tickets"].iloc[0])
    ticket_prom = float(df_kpi["ticket_promedio"].iloc[0])
    unidades = int(df_kpi["unidades"].iloc[0])

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ventas", f"${ventas_total:,.0f}")
    k2.metric("Tickets", f"{tickets:,}")
    k3.metric("Ticket promedio", f"${ticket_prom:,.0f}")
    k4.metric("Unidades", f"{unidades:,}")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("📆 Ventas por día (empleado)")
        df_ts = get_empleado_ventas_por_dia(date_from, date_to, id_emp, productos=productos_sel)
        if df_ts.empty:
            st.info("Sin ventas para este empleado con los filtros seleccionados.")
        else:
            fig = px.line(df_ts, x="dia", y="ventas_total", markers=True)
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("🏆 Top productos (empleado)")
        df_tp = get_empleado_top_productos(date_from, date_to, id_emp, limit=10)
        if df_tp.empty:
            st.info("Sin detalle de productos para este empleado.")
        else:
            fig = px.bar(df_tp, x="producto", y="unidades")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
