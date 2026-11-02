from app.repositories.db_connection import execute_query


def listar_servicios():
    sql = "SELECT id_servicio, nombre, descripcion, tipo, precio FROM servicios ORDER BY id_servicio"
    filas = execute_query(sql, fetchall=True)
    for fila in filas:
        fila["precio"] = float(fila["precio"])
    return filas
    