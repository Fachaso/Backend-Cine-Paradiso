from app.repositories.db_connection import execute_query

def obtener_usuario_por_id(id_usuario):
    return execute_query(
        "SELECT id_usuario, nombre, email, rol FROM usuarios WHERE id_usuario = %s",
        (id_usuario,),
        fetchone=True,
    )

def listar_compras_por_usuario(id_usuario):
    return execute_query(
        "SELECT id_compra, id_usuario, fecha_compra, monto_total, codigo_qr, estado_qr "
        "FROM compras WHERE id_usuario = %s ORDER BY fecha_compra DESC",
        (id_usuario,),
        fetchall=True,    
    ) or []