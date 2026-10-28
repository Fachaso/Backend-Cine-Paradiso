from mysql.connector import Error

from app.repositories.db_connection import get_db_connection


def listar_sucursales_activas():
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_sucursal, nombre, direccion "
            "FROM sucursales "
            "WHERE estado = 'ACTIVO' "
            "ORDER BY nombre ASC"
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def obtener_sucursal_por_id(id_sucursal):
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_sucursal FROM sucursales WHERE id_sucursal = %s",
            (id_sucursal,)
        )
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def listar_salas_por_sucursal(id_sucursal):
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_sala, id_sucursal, nombre, capacidad, estado "
            "FROM salas WHERE id_sucursal = %s ORDER BY nombre ASC",
            (id_sucursal,)
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def sala_existe_en_sucursal(id_sucursal, nombre):
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_sala FROM salas WHERE id_sucursal = %s AND nombre = %s",
            (id_sucursal, nombre)
        )
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def crear_sala_con_asientos(datos_sala, asientos):
    """Inserta sala y asientos en una única transacción de MySQL."""
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        conexion.start_transaction()
        cursor.execute(
            "INSERT INTO salas (id_sucursal, nombre, capacidad) VALUES (%s, %s, %s)",
            (datos_sala["id_sucursal"], datos_sala["nombre"], datos_sala["capacidad"])
        )
        id_sala = cursor.lastrowid

        for asiento in asientos:
            cursor.execute(
                "INSERT INTO asientos (id_sala, fila, numero, tipo, estado) "
                "VALUES (%s, %s, %s, %s, %s)",
                (id_sala, asiento["fila"], asiento["numero"], "NORMAL", "ACTIVO")
            )

        conexion.commit()
        return {
            "id_sala": id_sala,
            "id_sucursal": datos_sala["id_sucursal"],
            "nombre": datos_sala["nombre"],
            "capacidad": datos_sala["capacidad"],
            "asientos_creados": len(asientos),
        }
    except Exception:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
