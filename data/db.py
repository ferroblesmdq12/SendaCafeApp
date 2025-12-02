# Conexión reutilizable + helper para DataFrames

import psycopg2
import pandas as pd
from core.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT


def get_connection():
    """
    Devuelve una conexión a PostgreSQL en AWS RDS.
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn


def run_query_df(query: str, params=None) -> pd.DataFrame:
    """
    Ejecuta una consulta SQL y devuelve un DataFrame de pandas.
    """
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
    finally:
        conn.close()
    return df
