from app.repositories.db_connection import execute_query


def _convertir_servicio(fila):
    fila["precio"] = float(fila["precio"])
    return fila


def listar_servicios():
    sql = "SELECT id_servicio, nombre, descripcion, tipo, precio FROM servicios ORDER BY id_servicio"
    filas = execute_query(sql, fetchall=True)
    return [_convertir_servicio(fila) for fila in filas]


def obtener_servicio_por_id(id_servicio):
    sql = "SELECT id_servicio, nombre, descripcion, tipo, precio FROM servicios WHERE id_servicio = %s"
    fila = execute_query(sql, (id_servicio,), fetchone=True)

    if fila is None:
        return None

    return _convertir_servicio(fila)


def existe_servicio_con_nombre(nombre):
    sql = "SELECT id_servicio FROM servicios WHERE nombre = %s"
    return execute_query(sql, (nombre,), fetchone=True) is not None


def crear_servicio(nombre, descripcion, tipo, precio):
    sql = "INSERT INTO servicios (nombre, descripcion, tipo, precio) VALUES (%s, %s, %s, %s)"
    return execute_query(sql, (nombre, descripcion, tipo, precio), commit=True)