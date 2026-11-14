from app.repositories.db_connection import execute_query


def _convertir_resena(fila):
    fila["fecha"] = fila["fecha"].isoformat()
    return fila


def existe_pelicula(id_pelicula):
    sql = "SELECT id_pelicula FROM peliculas WHERE id_pelicula = %s"
    return execute_query(sql, (id_pelicula,), fetchone=True) is not None


def listar_resenas_por_pelicula(id_pelicula):
    sql = """
        SELECT r.id_resena, r.id_usuario, u.nombre AS nombre_usuario,
               r.id_pelicula, r.puntuacion, r.comentario, r.fecha
        FROM resenas AS r
        JOIN usuarios AS u ON u.id_usuario = r.id_usuario
        WHERE r.id_pelicula = %s
        ORDER BY r.fecha DESC, r.id_resena DESC
    """
    filas = execute_query(sql, (id_pelicula,), fetchall=True)
    return [_convertir_resena(fila) for fila in filas]


def usuario_asistio_a_pelicula(id_usuario, id_pelicula):
    sql = """
        SELECT 1
        FROM compras AS c
        JOIN entradas AS e ON e.id_compra = c.id_compra
        JOIN funciones AS f ON f.id_funcion = e.id_funcion
        WHERE c.id_usuario = %s
          AND f.id_pelicula = %s
          AND c.estado_qr = 'USADO'
        LIMIT 1
    """
    return execute_query(sql, (id_usuario, id_pelicula), fetchone=True) is not None


def existe_resena_de_usuario(id_usuario, id_pelicula):
    sql = "SELECT id_resena FROM resenas WHERE id_usuario = %s AND id_pelicula = %s"
    return execute_query(sql, (id_usuario, id_pelicula), fetchone=True) is not None


def crear_resena(id_usuario, id_pelicula, puntuacion, comentario):
    sql = """
        INSERT INTO resenas (id_usuario, id_pelicula, puntuacion, comentario)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(sql, (id_usuario, id_pelicula, puntuacion, comentario), commit=True)


def obtener_resena_por_id(id_resena):
    sql = """
        SELECT r.id_resena, r.id_usuario, u.nombre AS nombre_usuario,
               r.id_pelicula, r.puntuacion, r.comentario, r.fecha
        FROM resenas AS r
        JOIN usuarios AS u ON u.id_usuario = r.id_usuario
        WHERE r.id_resena = %s
    """
    fila = execute_query(sql, (id_resena,), fetchone=True)
    if fila is None:
        return None
    return _convertir_resena(fila)