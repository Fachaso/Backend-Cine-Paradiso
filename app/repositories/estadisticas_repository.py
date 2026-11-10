from app.repositories.db_connection import execute_query


def obtener_ocupacion_db(id_funcion=None, id_pelicula=None):
    """
    Consulta la capacidad y las entradas vendidas por funcion,
    permitiendo filtrar por id_funcion e id_pelicula.
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
        "SELECT f.id_funcion, p.titulo AS titulo_pelicula, "
        "s.nombre AS nombre_sala, f.fecha_hora, s.capacidad, "
        "COUNT(CASE "
        "WHEN c.estado_compra = 'CONFIRMADA' "
        "AND c.estado_qr IN ('PENDIENTE', 'USADO') "
        "THEN e.id_entrada "
        "END) AS entradas_vendidas "
        "FROM funciones f "
        "INNER JOIN peliculas p ON f.id_pelicula = p.id_pelicula "
        "INNER JOIN salas s ON f.id_sala = s.id_sala "
        "LEFT JOIN entradas e ON f.id_funcion = e.id_funcion "
        "LEFT JOIN compras c ON e.id_compra = c.id_compra "
    )

    if condiciones:
        consulta += "WHERE " + " AND ".join(condiciones) + " "

    consulta += (
        "GROUP BY f.id_funcion, p.titulo, s.nombre, "
        "f.fecha_hora, s.capacidad "
        "ORDER BY f.fecha_hora ASC"
    )

    resultado = execute_query(
        consulta,
        tuple(parametros),
        fetchall=True
    ) or []

    return resultado


def obtener_ventas_por_genero_db():
    """
    Obtiene el importe total y la cantidad de entradas vendidas
    por genero cinematografico.
    """
    consulta = (
        "SELECT p.genero, "
        "COALESCE(SUM(e.precio), 0.00) AS total_ventas, "
        "COUNT(e.id_entrada) AS entradas_vendidas "
        "FROM peliculas p "
        "INNER JOIN funciones f ON p.id_pelicula = f.id_pelicula "
        "INNER JOIN entradas e ON f.id_funcion = e.id_funcion "
        "INNER JOIN compras c ON e.id_compra = c.id_compra "
        "WHERE c.estado_compra = 'CONFIRMADA' "
        "AND c.estado_qr IN ('PENDIENTE', 'USADO') "
        "GROUP BY p.genero "
        "ORDER BY total_ventas DESC, entradas_vendidas DESC"
    )

    resultado = execute_query(
        consulta,
        fetchall=True
    ) or []

    return resultado


def obtener_franjas_horarias_db():
    """
    Obtiene la cantidad de entradas vendidas agrupadas
    segun el horario de las funciones.
    """
    consulta = (
        "SELECT DATE_FORMAT(f.fecha_hora, '%H:%i') AS hora, "
        "COUNT(e.id_entrada) AS entradas_vendidas "
        "FROM funciones f "
        "INNER JOIN entradas e ON f.id_funcion = e.id_funcion "
        "INNER JOIN compras c ON e.id_compra = c.id_compra "
        "WHERE c.estado_compra = 'CONFIRMADA' "
        "AND c.estado_qr IN ('PENDIENTE', 'USADO') "
        "GROUP BY DATE_FORMAT(f.fecha_hora, '%H:%i') "
        "ORDER BY entradas_vendidas DESC, hora ASC"
    )

    resultado = execute_query(
        consulta,
        fetchall=True
    ) or []

    return resultado


def obtener_cancelaciones_db():
    """
    Obtiene la cantidad total de compras cuyo QR
    se encuentra en estado CANCELADO.
    """
    consulta = (
        "SELECT COUNT(*) AS total_cancelaciones "
        "FROM compras "
        "WHERE estado_qr = 'CANCELADO'"
    )

    resultado = execute_query(
        consulta,
        fetchone=True
    )

    total_cancelaciones = 0

    if resultado:
        total_cancelaciones = resultado["total_cancelaciones"]

    return total_cancelaciones


def obtener_peliculas_mas_vistas_db(limit=5):
    """
    Obtiene las peliculas mas vistas segun la cantidad
    de entradas vendidas correspondientes a compras confirmadas.
    """
    consulta = (
        "SELECT p.id_pelicula, p.titulo, p.genero, "
        "COUNT(e.id_entrada) AS entradas_vendidas, "
        "COALESCE(SUM(e.precio), 0.00) AS total_recaudado "
        "FROM peliculas p "
        "INNER JOIN funciones f ON p.id_pelicula = f.id_pelicula "
        "INNER JOIN entradas e ON f.id_funcion = e.id_funcion "
        "INNER JOIN compras c ON e.id_compra = c.id_compra "
        "WHERE c.estado_compra = 'CONFIRMADA' "
        "AND c.estado_qr IN ('PENDIENTE', 'USADO') "
        "GROUP BY p.id_pelicula, p.titulo, p.genero "
        "ORDER BY entradas_vendidas DESC, total_recaudado DESC "
        "LIMIT %s"
    )

    resultado = execute_query(
        consulta,
        (limit,),
        fetchall=True
    ) or []

    return resultado