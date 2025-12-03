# pages/1_Dashboard.py

import streamlit as st
import plotly.express as px

from data.ventas_queries import (
    get_ventas_hoy,
    get_ventas_mes,
    get_ticket_promedio_mes,
    get_unidades_mes,
    get_ventas_ultimos_30_dias,
    get_ultimas_ventas,
    get_top_productos_mes,
    get_ventas_por_dia_ultimos_30,
    get_stock_critico,
)

st.set_page_config(page_title="Dashboard - Senda Café", layout="wide")

st.title("📊 Dashboard Senda Café")

st.markdown("### Resumen general")

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    ventas_hoy = get_ventas_hoy()
    col1.metric("Ventas HOY", f"${ventas_hoy:,.0f}")

with col2:
    ventas_mes = get_ventas_mes()
    col2.metric("Ventas MES", f"${ventas_mes:,.0f}")

with col3:
    ticket_promedio = get_ticket_promedio_mes()
    col3.metric("Ticket promedio MES", f"${ticket_promedio:,.0f}")

with col4:
    unidades_mes = get_unidades_mes()
    col4.metric("Unidades vendidas MES", f"{unidades_mes:,.0f}")

st.markdown("---")

# ---------------- Ventas por día (últimos 30) ----------------
st.subheader("📆 Ventas por día (últimos 30 días)")

df_dias = get_ventas_por_dia_ultimos_30()

if df_dias.empty:
    st.info("No hay ventas registradas en los últimos 30 días.")
else:
    fig_dias = px.line(
        df_dias,
        x="fecha",
        y="total",
        markers=True,
        title="Ingresos por día (últimos 30 días)"
    )
    st.plotly_chart(fig_dias, use_container_width=True)

# ---------------- Top productos + Últimas ventas ----------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🥐 Top productos del mes (por unidades)")

    df_top = get_top_productos_mes(limit=5)

    if df_top.empty:
        st.info("Todavía no hay productos vendidos este mes.")
    else:
        fig_top = px.bar(
            df_top,
            x="producto",
            y="unidades",
            title="Top productos del mes"
        )
        st.plotly_chart(fig_top, use_container_width=True)
        st.dataframe(df_top)

with col_right:
    st.subheader("🧾 Últimas ventas registradas")

    df_last = get_ultimas_ventas(limit=20)

    if df_last.empty:
        st.info("Todavía no hay ventas registradas.")
    else:
        st.dataframe(df_last)

# ---------------- Stock crítico ----------------
st.markdown("---")
st.subheader("⚠️ Stock crítico")

df_stock = get_stock_critico()

if df_stock.empty:
    st.success("No hay productos en estado crítico de stock. 🎉")
else:
    st.warning("Hay productos con stock bajo, revisar abastecimiento.")
    st.dataframe(df_stock)
