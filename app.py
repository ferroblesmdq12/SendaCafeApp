import streamlit as st
import plotly.express as px
from data.ventas_queries import (
    get_ventas_hoy,
    get_ventas_mes,
    get_ticket_promedio_mes,
    get_unidades_mes,
    get_ventas_ultimos_30_dias,
    get_ultimas_ventas
)

st.set_page_config(page_title="Senda Café", layout="wide")

st.title("☕ Senda Café – Dashboard conectado a AWS RDS")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas HOY", f"${get_ventas_hoy():,.0f}")
col2.metric("Ventas MES", f"${get_ventas_mes():,.0f}")
col3.metric("Ticket Promedio", f"${get_ticket_promedio_mes():,.0f}")
col4.metric("Unidades MES", f"{int(get_unidades_mes()):,}")

st.markdown("---")

st.subheader("📈 Ventas últimos 30 días")
df = get_ventas_ultimos_30_dias()
if df.empty:
    st.info("Sin ventas en los últimos 30 días.")
else:
    fig = px.line(df, x="fecha", y="total", markers=True)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🧾 Últimas ventas")
st.dataframe(get_ultimas_ventas(50), use_container_width=True)
