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


COLUMNAS_EDITABLES = ("nombre", "descripcion", "tipo", "precio")


def existe_otro_servicio_con_nombre(nombre, id_servicio):
    sql = "SELECT id_servicio FROM servicios WHERE nombre = %s AND id_servicio <> %s"
    return execute_query(sql, (nombre, id_servicio), fetchone=True) is not None


def actualizar_servicio(id_servicio, campos):
    columnas = [c for c in campos if c in COLUMNAS_EDITABLES]
    if not columnas:
        return
    asignaciones = ", ".join(f"{c} = %s" for c in columnas)
    valores = [campos[c] for c in columnas] + [id_servicio]
    sql = f"UPDATE servicios SET {asignaciones} WHERE id_servicio = %s"
    execute_query(sql, tuple(valores), commit=True)