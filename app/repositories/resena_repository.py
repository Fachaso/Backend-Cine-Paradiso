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
