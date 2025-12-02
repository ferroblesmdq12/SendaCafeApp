import streamlit as st
from data.db import run_query_df

st.set_page_config(page_title="Senda Café - Debug", layout="wide")

st.title("Debug Senda Café - Tablas")

st.subheader("Estructura de la tabla 'ventas'")

df_cols_ventas = run_query_df("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'ventas'
    ORDER BY ordinal_position;
""")
st.dataframe(df_cols_ventas, use_container_width=True)

st.subheader("Primeras filas de 'ventas'")
df_ventas = run_query_df("SELECT * FROM ventas LIMIT 5;")
st.dataframe(df_ventas, use_container_width=True)

st.subheader("Estructura de la tabla 'ventas_detalle'")
df_cols_detalle = run_query_df("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'ventas_detalle'
    ORDER BY ordinal_position;
""")
st.dataframe(df_cols_detalle, use_container_width=True)

st.subheader("Primeras filas de 'ventas_detalle'")
df_detalle = run_query_df("SELECT * FROM ventas_detalle LIMIT 5;")
st.dataframe(df_detalle, use_container_width=True)
