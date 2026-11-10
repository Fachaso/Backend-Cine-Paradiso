from app.repositories.db_connection import execute_query


def obtener_email_usuario(id_usuario):
    fila = execute_query(
        "SELECT email FROM usuarios WHERE id_usuario = %s",
        (id_usuario,),
        fetchone=True,
    )
    return fila["email"] if fila else None