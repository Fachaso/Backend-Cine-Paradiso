from app.repositories.db_connection import execute_query

def obtener_qr(codigo_qr):
    return execute_query(
        "SELECT id_compra, codigo_qr, estado_qr FROM compras WHERE codigo_qr = %s",
        (codigo_qr,),
        fetchone=True,    
    )

def qr_pertenece_a_funcion(codigo_qr, id_funcion):
    fila = execute_query(
        "SELECT 1 AS existe FROM compras c "
        "JOIN entradas e ON e.id_compra = c.id_compra "
        "WHERE c.codigo_qr = %s AND e.id_funcion = %s LIMIT 1",
        (codigo_qr, id_funcion),
        fetchone=True,
    )
    return fila is not None


def marcar_qr_usado(codigo_qr):
    return execute_query(
        "UPDATE compras SET estado_qr = 'USADO' WHERE codigo_qr = %s AND estado_qr = 'PENDIENTE'",
        (codigo_qr,),
        commit=True,
    )


def qr_en_horario(codigo_qr, id_funcion):
    fila = execute_query(
        "SELECT 1 AS existe FROM compras c "
        "JOIN entradas e ON e.id_compra = c.id_compra "
        "JOIN funciones f ON f.id_funcion = e.id_funcion "
        "JOIN peliculas p ON p.id_pelicula = f.id_pelicula "
        "WHERE c.codigo_qr = %s AND e.id_funcion = %s "
        "AND NOW() BETWEEN DATE_SUB(f.fecha_hora, INTERVAL 40 MINUTE) "
        "AND DATE_ADD(f.fecha_hora, INTERVAL p.duracion_min MINUTE) LIMIT 1",
        (codigo_qr, id_funcion),
        fetchone=True,
    )
    return fila is not None
