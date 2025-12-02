import os
from dotenv import load_dotenv

try:
    import streamlit as st
    STREAMLIT = True
except ImportError:
    STREAMLIT = False

# Local: carga .env
load_dotenv()

def get_env_var(key: str, default: str | None = None) -> str | None:
    # Si estamos en Streamlit Cloud y existe en secrets
    if STREAMLIT and hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    # Si no, toma de variables de entorno (.env/local)
    return os.getenv(key, default)


DB_HOST = get_env_var("DB_HOST")
DB_NAME = get_env_var("DB_NAME")
DB_USER = get_env_var("DB_USER")
DB_PASSWORD = get_env_var("DB_PASSWORD")
DB_PORT = get_env_var("DB_PORT", "5432")
