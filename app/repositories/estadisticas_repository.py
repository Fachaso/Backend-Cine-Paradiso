from app.repositories.db_connection import execute_query


def obtener_ocupacion_db(id_funcion=None, id_pelicula=None):
    """
    Consulta SQL pura para obtener el porcentaje de ocupación por función.
    """
    condiciones = []
    parametros = []

    if id_funcion is not None:
        condiciones.append("f.id_funcion = %s")
        parametros.append(id_funcion)

    if id_pelicula is not None:
        condiciones.append("f.id_pelicula = %s")
        parametros.append(id_pelicula)

    consulta = (
        "SELECT f.id_funcion, p.titulo AS titulo_pelicula, s.nombre AS nombre_sala, "
        "f.fecha_hora, s.capacidad, COUNT(DISTINCT e.id_entrada) AS entradas_vendidas "
        "FROM funciones f "
        "INNER JOIN peliculas p ON f.id_pelicula = p.id_pelicula "
        "INNER JOIN salas s ON f.id_sala = s.id_sala "
        "LEFT JOIN entradas e ON f.id_funcion = e.id_funcion "
        "LEFT JOIN compras c ON e.id_compra = c.id_compra AND c.estado_compra != 'CANCELADA' "
    )

    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)

    consulta += (
        " GROUP BY f.id_funcion, p.titulo, s.nombre, f.fecha_hora, s.capacidad "
        "ORDER BY f.fecha_hora ASC"
    )

    return execute_query(consulta, tuple(parametros), fetchall=True) or []


def obtener_ventas_por_genero_db():
    """
    Consulta SQL pura para agrupar ventas por género cinematográfico.
    """
    consulta = (
        "SELECT p.genero, COALESCE(SUM(e.precio), 0.00) AS total_ventas, "
        "COUNT(e.id_entrada) AS entradas_vendidas "
        "FROM peliculas p "
        "INNER JOIN funciones f ON p.id_pelicula = f.id_pelicula "
        "INNER JOIN entradas e ON f.id_funcion = e.id_funcion "
        "INNER JOIN compras c ON e.id_compra = c.id_compra "
        "WHERE c.estado_compra != 'CANCELADA' AND (c.estado_qr IS NULL OR c.estado_qr != 'CANCELADO') "
        "GROUP BY p.genero "
        "ORDER BY total_ventas DESC, entradas_vendidas DESC"
    )
    return execute_query(consulta, fetchall=True) or []


def obtener_franjas_horarias_db():
    """
    Consulta SQL pura para agrupar entradas vendidas por franja horaria.
    """
    consulta = (
        "SELECT DATE_FORMAT(f.fecha_hora, '%H:%i') AS hora, "
        "COUNT(e.id_entrada) AS entradas_vendidas "
        "FROM funciones f "
        "INNER JOIN entradas e ON f.id_funcion = e.id_funcion "
        "INNER JOIN compras c ON e.id_compra = c.id_compra "
        "WHERE c.estado_compra != 'CANCELADA' AND (c.estado_qr IS NULL OR c.estado_qr != 'CANCELADO') "
        "GROUP BY DATE_FORMAT(f.fecha_hora, '%H:%i') "
        "ORDER BY entradas_vendidas DESC, hora ASC"
    )
    return execute_query(consulta, fetchall=True) or []


def obtener_cancelaciones_db():
    """
    Consulta SQL pura para contar las compras canceladas.
    """
    consulta = (
        "SELECT COUNT(*) AS total_cancelaciones "
        "FROM compras "
        "WHERE estado_qr = 'CANCELADO'"
    )
    resultado = execute_query(consulta, fetchone=True)
    return resultado["total_cancelaciones"] if resultado else 0


def obtener_peliculas_mas_vistas_db(limit=5):
    """
    Consulta SQL pura para obtener el ranking de películas más vistas.
    """
    consulta = (
        "SELECT p.id_pelicula, p.titulo, p.genero, "
        "COUNT(e.id_entrada) AS entradas_vendidas, "
        "COALESCE(SUM(e.precio), 0.00) AS total_recaudado "
        "FROM peliculas p "
        "INNER JOIN funciones f ON p.id_pelicula = f.id_pelicula "
        "INNER JOIN entradas e ON f.id_funcion = e.id_funcion "
        "INNER JOIN compras c ON e.id_compra = c.id_compra "
        "WHERE c.estado_compra != 'CANCELADA' AND (c.estado_qr IS NULL OR c.estado_qr != 'CANCELADO') "
        "GROUP BY p.id_pelicula, p.titulo, p.genero "
        "ORDER BY entradas_vendidas DESC, total_recaudado DESC "
        "LIMIT %s"
    )
    return execute_query(consulta, (limit,), fetchall=True) or []
