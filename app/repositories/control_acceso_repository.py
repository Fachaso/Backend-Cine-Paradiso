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


def obtener_qr_con_funcion(codigo_qr):
    filas = execute_query(
        "SELECT c.codigo_qr, c.estado_qr, e.id_funcion, "
        "p.titulo AS pelicula_titulo, s.nombre AS sala_nombre, "
        "f.fecha_hora, a.fila, a.numero "
        "FROM compras c "
        "JOIN entradas e ON e.id_compra = c.id_compra "
        "JOIN funciones f ON f.id_funcion = e.id_funcion "
        "JOIN peliculas p ON p.id_pelicula = f.id_pelicula "
        "JOIN salas s ON s.id_sala = f.id_sala "
        "JOIN asientos a ON a.id_asiento = e.id_asiento "
        "WHERE c.codigo_qr = %s",
        (codigo_qr,),
        fetchone=True,
    )
    if filas is None:
        return None

    butacas = []
    id_funcion = filas["id_funcion"]

    todas_filas = execute_query(
        "SELECT a.fila, a.numero "
        "FROM compras c "
        "JOIN entradas e ON e.id_compra = c.id_compra "
        "JOIN asientos a ON a.id_asiento = e.id_asiento "
        "WHERE c.codigo_qr = %s",
        (codigo_qr,),
        fetchall=True,
    )
    for f in (todas_filas or []):
        butacas.append(f"{f['fila']}{f['numero']}")
    return {
        "codigo_qr": filas["codigo_qr"],
        "estado_qr": filas["estado_qr"],
        "id_funcion": id_funcion,
        "pelicula_titulo": filas["pelicula_titulo"],
        "sala_nombre": filas["sala_nombre"],
        "fecha_hora": str(filas["fecha_hora"]),
        "butacas": butacas,
    }