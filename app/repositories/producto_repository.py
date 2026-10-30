from app.repositories.db_connection import execute_query


def obtener_productos_activos_por_ids(ids_productos):
    """
    Obtiene los productos activos cuyos identificadores
    se encuentran en la lista recibida.
    """

    if not ids_productos:
        return []

    placeholders = ", ".join(["%s"] * len(ids_productos))

    sql = f"""
        SELECT id_producto, nombre, tipo, precio_base, estado
        FROM productos
        WHERE estado = 'ACTIVO'
          AND id_producto IN ({placeholders})
    """

    return execute_query(
        sql,
        tuple(ids_productos),
        fetchall=True
    )