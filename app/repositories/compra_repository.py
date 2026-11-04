from app.repositories.db_connection import get_db_connection
from uuid import uuid4
from decimal import Decimal
from mysql.connector import IntegrityError


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




def _error_compra(codigo, mensaje, codigo_http):
    return None, {"code": codigo, "message": mensaje}, codigo_http


def _marcar_compra_expirada(cursor, id_compra):
    cursor.execute(
        """UPDATE compras SET estado_compra = 'EXPIRADA'
        WHERE id_compra = %s AND estado_compra = 'PENDIENTE'""",
        (id_compra,)
    )
    cursor.execute(
        """UPDATE bloqueos_asientos SET estado = 'EXPIRADO'
        WHERE id_compra = %s AND estado = 'ACTIVO'""",
        (id_compra,)
    )


def _limpiar_compra_pendiente(cursor, id_compra):
    if cursor is not None and id_compra is not None:
        cursor.execute(
            """DELETE FROM compras WHERE id_compra = %s
            AND estado_compra = 'PENDIENTE'""",
            (id_compra,)
        )


def eliminar_compra_pendiente(id_compra):
    conexion = cursor = None
    try:
        conexion = get_db_connection()
        conexion.autocommit = True
        cursor = conexion.cursor()
        cursor.execute(
            """DELETE FROM compras WHERE id_compra = %s
            AND estado_compra = 'PENDIENTE'""",
            (id_compra,)
        )
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()


def _limpiar_confirmacion(cursor, id_compra):
    cursor.execute(
        "SELECT estado_compra FROM compras WHERE id_compra = %s",
        (id_compra,)
    )
    compra = cursor.fetchone()
    if compra is None or compra["estado_compra"] != "PENDIENTE":
        return
    cursor.execute("DELETE FROM detalle_compra_servicios WHERE id_compra = %s", (id_compra,))
    cursor.execute("DELETE FROM entradas WHERE id_compra = %s", (id_compra,))


def crear_compra_pendiente(id_usuario, datos):
    conexion = cursor = None
    id_compra = None
    try:
        conexion = get_db_connection()
        conexion.autocommit = True
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_sala, precio_entrada FROM funciones WHERE id_funcion = %s",
            (datos["id_funcion"],)
        )
        funcion = cursor.fetchone()
        if funcion is None:
            return _error_compra("FUNCION_NO_ENCONTRADA", "La función no existe", 404)

        ids = datos["asientos_ids"]
        marcas = ", ".join(["%s"] * len(ids))
        cursor.execute(
            f"SELECT id_asiento FROM asientos WHERE id_sala = %s AND id_asiento IN ({marcas})",
            (funcion["id_sala"], *ids)
        )
        if {r["id_asiento"] for r in cursor.fetchall()} != set(ids):
            return _error_compra(
                "ASIENTOS_INVALIDOS",
                "Uno o más asientos no pertenecen a la sala de la función",
                400
            )
        cursor.execute(
            f"SELECT id_asiento FROM entradas WHERE id_funcion = %s AND id_asiento IN ({marcas})",
            (datos["id_funcion"], *ids)
        )
        if cursor.fetchall():
            return _error_compra(
                "ASIENTO_NO_DISPONIBLE", "Uno o más asientos ya fueron vendidos", 409
            )

        precio = funcion["precio_entrada"]
        total = precio * len(ids)
        cursor.execute(
            """INSERT INTO compras
            (id_usuario, monto_total, estado_compra, codigo_qr, estado_qr)
            VALUES (%s, %s, 'PENDIENTE', NULL, NULL)""",
            (id_usuario, total)
        )
        id_compra = cursor.lastrowid

        for id_asiento in ids:
            cursor.execute(
                """SELECT id_compra FROM bloqueos_asientos
                WHERE id_funcion = %s AND id_asiento = %s
                AND (estado IN ('EXPIRADO', 'LIBERADO')
                    OR (estado = 'ACTIVO' AND vence_en <= NOW()))""",
                (datos["id_funcion"], id_asiento)
            )
            anterior = cursor.fetchone()
            if anterior:
                cursor.execute(
                    """UPDATE compras SET estado_compra = 'EXPIRADA'
                    WHERE id_compra = %s AND estado_compra = 'PENDIENTE'""",
                    (anterior["id_compra"],)
                )

            cursor.execute(
                """UPDATE bloqueos_asientos
                SET id_compra = %s, precio_entrada = %s,
                    vence_en = DATE_ADD(NOW(), INTERVAL 10 MINUTE),
                    estado = 'ACTIVO'
                WHERE id_funcion = %s AND id_asiento = %s
                AND (estado IN ('EXPIRADO', 'LIBERADO')
                    OR (estado = 'ACTIVO' AND vence_en <= NOW()))""",
                (id_compra, precio, datos["id_funcion"], id_asiento)
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    """INSERT INTO bloqueos_asientos
                    (id_funcion, id_asiento, id_compra, precio_entrada, vence_en, estado)
                    VALUES (%s, %s, %s, %s, DATE_ADD(NOW(), INTERVAL 10 MINUTE), 'ACTIVO')""",
                    (datos["id_funcion"], id_asiento, id_compra, precio)
                )

        return {
            "id_compra": id_compra,
            "estado_compra": "PENDIENTE",
            "monto_total": total,
        }, None, 201
    except IntegrityError as error:
        _limpiar_compra_pendiente(cursor, id_compra)
        if error.errno == 1062:
            return _error_compra(
                "ASIENTO_NO_DISPONIBLE",
                "Otro cliente acaba de reservar uno de los asientos",
                409
            )
        raise
    except Exception:
        _limpiar_compra_pendiente(cursor, id_compra)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()


def confirmar_compra(id_compra, id_usuario, datos):
    conexion = cursor = None
    try:
        conexion = get_db_connection()
        conexion.autocommit = True
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """SELECT id_compra, id_usuario, monto_total, estado_compra, codigo_qr
            FROM compras WHERE id_compra = %s""",
            (id_compra,)
        )
        compra = cursor.fetchone()
        if compra is None or compra["id_usuario"] != id_usuario:
            return _error_compra("COMPRA_NO_ENCONTRADA", "La compra no existe", 404)
        if compra["estado_compra"] == "CONFIRMADA":
            return compra, None, 200
        if compra["estado_compra"] != "PENDIENTE":
            return _error_compra(
                "COMPRA_NO_PENDIENTE", "La compra no se encuentra pendiente", 409
            )

        cursor.execute(
            """SELECT id_funcion, id_asiento, precio_entrada, estado,
                vence_en > NOW() AS vigente
            FROM bloqueos_asientos WHERE id_compra = %s""",
            (id_compra,)
        )
        asientos = cursor.fetchall()
        if not asientos or any(
            a["estado"] != "ACTIVO" or not a["vigente"] for a in asientos
        ):
            _marcar_compra_expirada(cursor, id_compra)
            return _error_compra(
                "COMPRA_EXPIRADA", "El plazo para confirmar la compra venció", 409
            )

        servicios = datos["servicios"]
        ids_servicios = [s["id_servicio"] for s in servicios]
        precios = {}
        if ids_servicios:
            marcas = ", ".join(["%s"] * len(ids_servicios))
            cursor.execute(
                f"SELECT id_servicio, precio FROM servicios WHERE id_servicio IN ({marcas})",
                tuple(ids_servicios)
            )
            precios = {s["id_servicio"]: s["precio"] for s in cursor.fetchall()}
            for servicio in servicios:
                if servicio["id_servicio"] not in precios:
                    return _error_compra(
                        "SERVICIO_NO_ENCONTRADO",
                        f"El servicio {servicio['id_servicio']} no existe",
                        404
                    )

        total = sum((a["precio_entrada"] for a in asientos), Decimal("0.00"))
        for servicio in servicios:
            total += precios[servicio["id_servicio"]] * servicio["cantidad"]

        # El UNIQUE (id_funcion, id_asiento) resuelve la carrera al emitir entradas.
        cursor.execute(
            """INSERT INTO entradas (id_compra, id_funcion, id_asiento, precio)
            SELECT b.id_compra, b.id_funcion, b.id_asiento, b.precio_entrada
            FROM bloqueos_asientos b
            WHERE b.id_compra = %s AND b.estado = 'ACTIVO'
                AND b.vence_en > NOW()""",
            (id_compra,)
        )
        if cursor.rowcount != len(asientos):
            _limpiar_confirmacion(cursor, id_compra)
            _marcar_compra_expirada(cursor, id_compra)
            return _error_compra(
                "COMPRA_EXPIRADA", "El plazo para confirmar la compra venció", 409
            )

        try:
            if servicios:
                cursor.executemany(
                    """INSERT INTO detalle_compra_servicios
                    (id_compra, id_servicio, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)""",
                    [
                        (id_compra, s["id_servicio"], s["cantidad"],
                         precios[s["id_servicio"]])
                        for s in servicios
                    ]
                )
        except Exception:
            _limpiar_confirmacion(cursor, id_compra)
            raise

        qr = str(uuid4())
        cursor.execute(
            """UPDATE compras SET estado_compra = 'CONFIRMADA',
                monto_total = %s, codigo_qr = %s, estado_qr = 'PENDIENTE'
            WHERE id_compra = %s AND id_usuario = %s
                AND estado_compra = 'PENDIENTE'""",
            (total, qr, id_compra, id_usuario)
        )
        if cursor.rowcount != 1:
            _limpiar_confirmacion(cursor, id_compra)
            return _error_compra(
                "COMPRA_NO_PENDIENTE", "La compra cambió de estado", 409
            )
        cursor.execute(
            """UPDATE bloqueos_asientos SET estado = 'CONFIRMADO'
            WHERE id_compra = %s AND estado = 'ACTIVO'""",
            (id_compra,)
        )
        return {
            "id_compra": id_compra,
            "estado_compra": "CONFIRMADA",
            "monto_total": total,
            "codigo_qr": qr,
            "estado_qr": "PENDIENTE",
        }, None, 200
    except IntegrityError as error:
        if cursor is not None and error.errno == 1062:
            cursor.execute(
                """SELECT estado_compra, monto_total, codigo_qr FROM compras
                WHERE id_compra = %s AND id_usuario = %s""",
                (id_compra, id_usuario)
            )
            actual = cursor.fetchone()
            if actual and actual["estado_compra"] == "CONFIRMADA":
                return {
                    "id_compra": id_compra,
                    "estado_compra": "CONFIRMADA",
                    "monto_total": actual["monto_total"],
                    "codigo_qr": actual["codigo_qr"],
                }, None, 200
            cursor.execute(
                "SELECT COUNT(*) AS cantidad FROM entradas WHERE id_compra = %s",
                (id_compra,)
            )
            if actual and cursor.fetchone()["cantidad"] == 0:
                _marcar_compra_expirada(cursor, id_compra)
            return _error_compra(
                "ASIENTO_NO_DISPONIBLE", "Uno o más asientos ya fueron vendidos", 409
            )
        raise
    except Exception:
        if cursor is not None:
            _limpiar_confirmacion(cursor, id_compra)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()




def cancelar_compra(id_compra, id_usuario):
    conexion = cursor = None
    try:
        conexion = get_db_connection()
        conexion.autocommit = True
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """SELECT id_compra, id_usuario, estado_compra, estado_qr
            FROM compras WHERE id_compra = %s""",
            (id_compra,)
        )
        compra = cursor.fetchone()
        if compra is None or compra["id_usuario"] != id_usuario:
            return _error_compra("COMPRA_NO_ENCONTRADA", "La compra no existe", 404)

        if compra["estado_compra"] == "CANCELADA":
            cursor.execute("DELETE FROM entradas WHERE id_compra = %s", (id_compra,))
            cursor.execute(
                """UPDATE bloqueos_asientos SET estado = 'LIBERADO'
                WHERE id_compra = %s
                    AND estado IN ('ACTIVO', 'CONFIRMADO', 'EXPIRADO')""",
                (id_compra,)
            )
            return compra, None, 200

        if compra["estado_compra"] == "PENDIENTE":
            cursor.execute(
                """UPDATE compras SET estado_compra = 'CANCELADA'
                WHERE id_compra = %s AND estado_compra = 'PENDIENTE'""",
                (id_compra,)
            )
            cursor.execute(
                """UPDATE bloqueos_asientos SET estado = 'LIBERADO'
                WHERE id_compra = %s AND estado = 'ACTIVO'""",
                (id_compra,)
            )
            return {
                "id_compra": id_compra,
                "estado_compra": "CANCELADA",
                "estado_qr": None,
            }, None, 200

        if (
            compra["estado_compra"] != "CONFIRMADA"
            or compra["estado_qr"] != "PENDIENTE"
        ):
            return _error_compra(
                "COMPRA_NO_CANCELABLE",
                "La compra no se puede cancelar en su estado actual",
                409
            )

        cursor.execute(
            """SELECT COUNT(*) AS iniciadas
            FROM entradas e
            JOIN funciones f ON f.id_funcion = e.id_funcion
            WHERE e.id_compra = %s AND f.fecha_hora <= NOW()""",
            (id_compra,)
        )
        if cursor.fetchone()["iniciadas"] > 0:
            return _error_compra(
                "COMPRA_NO_CANCELABLE",
                "No se puede cancelar después del inicio de la función",
                409
            )

        cursor.execute(
            """UPDATE compras SET estado_compra = 'CANCELADA',
                estado_qr = 'CANCELADO'
            WHERE id_compra = %s AND id_usuario = %s
                AND estado_compra = 'CONFIRMADA'
                AND estado_qr = 'PENDIENTE'""",
            (id_compra, id_usuario)
        )
        if cursor.rowcount != 1:
            return _error_compra(
                "COMPRA_NO_CANCELABLE", "La compra cambió de estado", 409
            )
        cursor.execute("DELETE FROM entradas WHERE id_compra = %s", (id_compra,))
        cursor.execute(
            """UPDATE bloqueos_asientos SET estado = 'LIBERADO'
            WHERE id_compra = %s AND estado = 'CONFIRMADO'""",
            (id_compra,)
        )
        return {
            "id_compra": id_compra,
            "estado_compra": "CANCELADA",
            "estado_qr": "CANCELADO",
        }, None, 200
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()


def obtener_compra(id_compra, id_usuario):
    conexion = cursor = None
    try:
        conexion = get_db_connection()
        conexion.autocommit = True
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """UPDATE compras AS c SET c.estado_compra = 'EXPIRADA'
            WHERE c.id_compra = %s AND c.estado_compra = 'PENDIENTE'
            AND EXISTS (
                SELECT 1 FROM bloqueos_asientos b
                WHERE b.id_compra = c.id_compra AND b.estado = 'ACTIVO'
                    AND b.vence_en <= NOW()
            )""",
            (id_compra,)
        )
        cursor.execute(
            """UPDATE bloqueos_asientos SET estado = 'EXPIRADO'
            WHERE id_compra = %s AND estado = 'ACTIVO' AND vence_en <= NOW()""",
            (id_compra,)
        )
        cursor.execute(
            """SELECT id_compra, id_usuario, fecha_compra, monto_total,
                estado_compra, codigo_qr, estado_qr FROM compras
            WHERE id_compra = %s AND id_usuario = %s""",
            (id_compra, id_usuario)
        )
        compra = cursor.fetchone()
        if compra is None:
            return _error_compra("COMPRA_NO_ENCONTRADA", "La compra no existe", 404)

        if compra["estado_compra"] == "CONFIRMADA":
            cursor.execute(
                """SELECT e.id_entrada, e.id_compra, e.id_funcion, e.id_asiento,
                    a.fila, a.numero, e.precio
                FROM entradas e JOIN asientos a ON a.id_asiento = e.id_asiento
                WHERE e.id_compra = %s ORDER BY e.id_entrada""",
                (id_compra,)
            )
            compra["entradas"] = cursor.fetchall()
            cursor.execute(
                """SELECT d.id_detalle, d.id_compra, d.id_servicio,
                    s.nombre AS nombre_servicio, d.cantidad, d.precio_unitario
                FROM detalle_compra_servicios d
                JOIN servicios s ON s.id_servicio = d.id_servicio
                WHERE d.id_compra = %s ORDER BY d.id_detalle""",
                (id_compra,)
            )
            compra["servicios"] = cursor.fetchall()
        else:
            cursor.execute(
                """SELECT NULL AS id_entrada, b.id_compra, b.id_funcion,
                    b.id_asiento, a.fila, a.numero, b.precio_entrada AS precio,
                    b.vence_en
                FROM bloqueos_asientos b
                JOIN asientos a ON a.id_asiento = b.id_asiento
                WHERE b.id_compra = %s ORDER BY b.id_funcion, b.id_asiento""",
                (id_compra,)
            )
            compra["entradas"] = cursor.fetchall()
            compra["servicios"] = []
        return compra, None, 200
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()
