from app.repositories.db_connection import execute_query


def buscar_por_email(email):
    return execute_query(
        "SELECT id_usuario, nombre, email, password_hash, rol FROM usuarios WHERE email = %s",
        (email,),
        fetchone=True,
    )


def buscar_por_id(id_usuario):
    return execute_query(
        "SELECT id_usuario, nombre, email, rol FROM usuarios WHERE id_usuario = %s",
        (id_usuario,),
        fetchone=True,
    )


def crear_usuario(nombre, email, password_hash, rol="CLIENTE"):
    return execute_query(
        "INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, %s)",
        (nombre, email, password_hash, rol),
        commit=True,
)