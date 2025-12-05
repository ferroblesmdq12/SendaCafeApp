# data/usuarios_queries.py

import bcrypt
from data.db import get_connection   # ya lo tenés en tu proyecto


def get_user_by_email_or_username(identifier: str):
    """
    Permite loguearse usando email O usuario.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_usuario,
               nombre,
               email,
               usuario,
               hash_password,
               rol,
               activo
        FROM usuarios
        WHERE email = %s OR usuario = %s;
    """, (identifier, identifier))

    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def authenticate(identifier: str, password: str):
    """
    identifier = email o usuario
    password   = contraseña que escribe el usuario
    """
    row = get_user_by_email_or_username(identifier)

    if row is None:
        return None

    id_usuario, nombre, email, usuario, hash_password, rol, activo = row

    if not activo:
        return None

    # Comparamos contraseña ingresada vs hash guardado
    if bcrypt.checkpw(password.encode("utf-8"), hash_password.encode("utf-8")):
        return {
            "id_usuario": id_usuario,
            "nombre": nombre,
            "email": email,
            "usuario": usuario,
            "rol": rol  # 'admin' o 'owner'
        }

    return None
