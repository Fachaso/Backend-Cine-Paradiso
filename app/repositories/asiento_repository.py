from app.repositories.db_connection import get_db_connection


def obtener_asientos_por_funcion(id_funcion, id_sala):
    asientos = None
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        consulta = (
            "SELECT a.id_asiento, a.fila, a.numero, "
            "CASE "
            "    WHEN e.id_asiento IS NOT NULL THEN 'OCUPADO' "
            "    ELSE 'DISPONIBLE' "
            "END AS estado "
            "FROM asientos a "
            "LEFT JOIN entradas e "
            "    ON a.id_asiento = e.id_asiento AND e.id_funcion = %s "
            "WHERE a.id_sala = %s "
            "ORDER BY a.fila ASC, a.numero ASC"
        )

        cursor.execute(consulta, (id_funcion, id_sala))
        asientos = cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return asientos
