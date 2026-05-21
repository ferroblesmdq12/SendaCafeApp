import psycopg2
import pandas as pd
from core.config import DATABASE_URL


def get_connection():
    """
    Devuelve una conexión a PostgreSQL en Neon.
    """
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL no está configurada.")

    conn = psycopg2.connect(DATABASE_URL)
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