import os
from dotenv import load_dotenv

try:
    import streamlit as st
    STREAMLIT = True
except ImportError:
    STREAMLIT = False

load_dotenv()

def get_env_var(key: str, default: str | None = None) -> str | None:
    if STREAMLIT:
        try:
            if key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass

    return os.getenv(key, default)

DATABASE_URL = get_env_var("DATABASE_URL")