from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("Intentando conectar a Neon...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("SELECT NOW();")
    result = cur.fetchone()

    print("Conexión exitosa a Neon PostgreSQL")
    print("Fecha/hora DB:", result)

    cur.close()
    conn.close()

except Exception as e:
    print("Error al conectar:")
    print(e)