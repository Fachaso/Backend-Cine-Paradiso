from app.repositories.db_connection import execute_query

def obtener_usuario_por_id(id_usuario):
    return execute_query(
        "SELECT id_usuario, nombre, email, rol FROM usuarios WHERE id_usuario = %s",
        (id_usuario,),
        fetchone=True,
    )

def listar_compras_por_usuario(id_usuario):
    return execute_query(
        "SELECT c.id_compra, c.id_usuario, c.fecha_compra, c.monto_total, c.codigo_qr, "
        "c.estado_compra, c.estado_qr, "
        "COALESCE((SELECT MAX(DATE_ADD(f.fecha_hora, INTERVAL p.duracion_min MINUTE) <= NOW()) "
        "FROM bloqueos_asientos b "
        "JOIN funciones f ON f.id_funcion = b.id_funcion "
        "JOIN peliculas p ON p.id_pelicula = f.id_pelicula "
        "WHERE b.id_compra = c.id_compra), 0) AS funcion_finalizada "
        "FROM compras c WHERE c.id_usuario = %s ORDER BY c.fecha_compra DESC",
        (id_usuario,),
        fetchall=True,
    ) or []
