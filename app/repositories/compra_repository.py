from app.repositories.db_connection import get_db_connection


def crear_orden_candybar(
    id_usuario,
    id_sucursal_retiro,
    productos,
    total,
    vencimiento_bloqueo
):
    """
    Crea una orden independiente de Candy Bar y sus detalles
    dentro de una única transacción.
    """

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        conn.start_transaction()

        cursor = conn.cursor()

        sql_orden = """
            INSERT INTO ordenes (
                tipo_orden,
                id_usuario,
                id_funcion,
                id_sucursal_retiro,
                vencimiento_bloqueo,
                estado,
                total
            )
            VALUES (
                'CANDYBAR_EXPRESS',
                %s,
                NULL,
                %s,
                %s,
                'PENDIENTE',
                %s
            )
        """

        cursor.execute(
            sql_orden,
            (
                id_usuario,
                id_sucursal_retiro,
                vencimiento_bloqueo,
                total
            )
        )

        id_orden = cursor.lastrowid

        sql_detalle = """
            INSERT INTO detalle_orden_productos (
                id_orden,
                id_producto,
                cantidad,
                precio_unitario
            )
            VALUES (%s, %s, %s, %s)
        """

        for producto in productos:
            cursor.execute(
                sql_detalle,
                (
                    id_orden,
                    producto["id_producto"],
                    producto["cantidad"],
                    producto["precio_unitario"]
                )
            )

        conn.commit()

        return id_orden

    except Exception:
        if conn is not None and conn.is_connected():
            conn.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()