from app.repositories.db_connection import execute_query


def buscar_usuario_por_email(email):
    return execute_query(
        "SELECT id_usuario, nombre, email, password_hash, rol FROM usuarios WHERE email = %s",
        (email,),
        fetchone=True,
    )


def actualizar_password(id_usuario, nuevo_password_hash):
    return execute_query(
        "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s",
        (nuevo_password_hash, id_usuario),
        commit=True,
    )