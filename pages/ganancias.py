import streamlit as st
import plotly.express as px
from datetime import date, timedelta

from services.ui_helpers import require_login, logout_button, sidebar_menu
from data.ventas_queries import (
    get_ventas_resumen_filtrado,
    get_costos_fijos_total_filtrado,
    get_ganancias_por_dia,
)

st.set_page_config(page_title="Ganancias - Senda Café", layout="wide")

def main():
    sidebar_menu()
    require_login(roles=["admin", "owner"])

    st.title("💰 Ganancias")
    logout_button()

    today = date.today()
    default_from = today - timedelta(days=30)

    f1, f2 = st.columns(2)
    with f1:
        date_from = st.date_input("Desde", value=default_from)
    with f2:
        date_to = st.date_input("Hasta", value=today)

    if date_from > date_to:
        st.error("Rango inválido: 'Desde' no puede ser mayor que 'Hasta'.")
        st.stop()

    # Ingresos (ventas)
    df_v = get_ventas_resumen_filtrado(date_from, date_to, empleados=[], productos=[])
    ingresos = float(df_v["ventas_total"].sum()) if not df_v.empty else 0.0

    # Costos
    try:
        costos = float(get_costos_fijos_total_filtrado(date_from, date_to))
    except Exception as e:
        st.error("No se pudo calcular costos. Verificá que exista la tabla 'costos_fijos' con columnas (fecha, monto).")
        st.stop()

    ganancia = ingresos - costos
    margen = (ganancia / ingresos) if ingresos > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ingresos", f"${ingresos:,.0f}")
    k2.metric("Costos fijos", f"${costos:,.0f}")
    k3.metric("Ganancia", f"${ganancia:,.0f}")
    k4.metric("Margen", f"{margen*100:,.1f}%")

    st.divider()

    st.subheader("📈 Evolución diaria (Ventas vs Costos vs Ganancia)")
    df = get_ganancias_por_dia(date_from, date_to)
    if df.empty:
        st.info("No hay datos para el período seleccionado.")
        return

    # 3 gráficos simples (más claro que un gráfico con 3 series para negocio)
    c1, c2, c3 = st.columns(3)

    with c1:
        fig = px.line(df, x="dia", y="ventas_total", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.line(df, x="dia", y="costos_total", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        fig = px.line(df, x="dia", y="ganancia", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Tabla")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Descargar (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="ganancias_por_dia.csv",
        mime="text/csv",
    )

if __name__ == "__main__":
    main()
