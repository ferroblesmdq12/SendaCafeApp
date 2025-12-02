from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()  # lee el .env

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

print("Intentando conectar a la base...")
print(f"Host: {DB_HOST}")
print(f"DB: {DB_NAME}")
print(f"User: {DB_USER}")
print(f"Port: {DB_PORT}")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    print("Conexión exitosa a PostgreSQL en AWS RDS")
    conn.close()
except Exception as e:
    print("Error al conectar:")
    print(e)
