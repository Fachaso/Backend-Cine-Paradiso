from app.repositories.db_connection import get_db_connection


def obtener_asientos_por_funcion(id_funcion, id_sala):
    asientos = None
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        consulta = (
            "SELECT asientos.id_asiento, asientos.fila, asientos.numero, asientos.columna, "
            "CASE "
            "    WHEN entradas.id_asiento IS NOT NULL THEN 'OCUPADO' "
            "    WHEN bloqueos_asientos.id_asiento IS NOT NULL THEN 'OCUPADO' "
            "    ELSE 'DISPONIBLE' "
            "END AS estado "
            "FROM asientos "
            "LEFT JOIN entradas "
            "    ON asientos.id_asiento = entradas.id_asiento "
            "    AND entradas.id_funcion = %s "
            "LEFT JOIN bloqueos_asientos "
            "    ON asientos.id_asiento = bloqueos_asientos.id_asiento "
            "    AND bloqueos_asientos.id_funcion = %s "
            "    AND bloqueos_asientos.estado = 'ACTIVO' "
            "    AND bloqueos_asientos.vence_en > NOW() "
            "WHERE asientos.id_sala = %s "
            "ORDER BY CHAR_LENGTH(asientos.fila) ASC, asientos.fila ASC, asientos.columna ASC"
        )

        cursor.execute(consulta, (id_funcion, id_funcion, id_sala))
        asientos = cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return asientos