import streamlit as st
import plotly.express as px
from datetime import date, timedelta

from services.ui_helpers import require_login, logout_button, sidebar_menu
from data.ventas_queries import (
    get_ventas_resumen_filtrado,
    get_costos_fijos_total_filtrado,
    get_ganancias_por_mes,
)

st.set_page_config(page_title="Ganancias - Senda Café", layout="wide")


def main():
    sidebar_menu()
    require_login(roles=["admin", "owner", "viewer"])

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

    # ======================
    # Ingresos
    # ======================

    df_v = get_ventas_resumen_filtrado(
        date_from,
        date_to,
        empleados=[],
        productos=[]
    )

    ingresos = float(df_v["ventas_total"].sum()) if not df_v.empty else 0.0

    # ======================
    # Costos
    # ======================

    try:
        costos = float(
            get_costos_fijos_total_filtrado(date_from, date_to)
        )

    except Exception:
        st.error(
            "No se pudo calcular costos. "
            "Verificá que exista la tabla "
            "'costos_fijos' con columnas (fecha, monto)."
        )
        st.stop()

    # ======================
    # KPIs
    # ======================

    ganancia = ingresos - costos
    margen = (ganancia / ingresos) if ingresos > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Ingresos", f"${ingresos:,.0f}")
    k2.metric("Costos fijos", f"${costos:,.0f}")
    k3.metric("Ganancia", f"${ganancia:,.0f}")
    k4.metric("Margen", f"{margen * 100:,.1f}%")

    st.divider()

    # ======================
    # Evolución mensual
    # ======================

    st.subheader("📈 Evolución mensual (Ventas vs Costos vs Ganancia)")

    df = get_ganancias_por_mes(date_from, date_to)

    if df.empty:
        st.info("No hay datos para el período seleccionado.")
        return

    # ======================
    # Transformación para gráfico combinado
    # ======================

    df_chart = df.melt(
        id_vars="mes",
        value_vars=[
            "ventas_total",
            "costos_total",
            "ganancia"
        ],
        var_name="indicador",
        value_name="monto"
    )

    df_chart["indicador"] = df_chart["indicador"].replace({
        "ventas_total": "Ventas",
        "costos_total": "Costos",
        "ganancia": "Ganancia"
    })

    # ======================
    # Gráfico
    # ======================

    fig = px.line(
        df_chart,
        x="mes",
        y="monto",
        color="indicador",
        markers=True,
        title="Ventas vs Costos vs Ganancia"
    )

    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Monto ARS",
        legend_title="Indicador",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ======================
    # Tabla
    # ======================

    st.subheader("📋 Tabla")

    st.dataframe(df, use_container_width=True)

    # ======================
    # Descarga CSV
    # ======================

    st.download_button(
        "⬇️ Descargar (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="ganancias_por_mes.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()