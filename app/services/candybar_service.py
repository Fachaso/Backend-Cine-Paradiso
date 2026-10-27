from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from app.repositories.db_connection import execute_query
from app.repositories.producto_repository import (
    obtener_productos_activos_por_ids
)
from app.repositories.compra_repository import crear_orden_candybar


def crear_pedido_candybar(datos):
    """
    Valida los datos y crea un pedido independiente del Candy Bar.

    Retorna un diccionario con el resultado de la operación.
    """

    if not isinstance(datos, dict):
        return {
            "status": "error",
            "message": "El cuerpo de la petición debe ser un objeto JSON."
        }, 400

    id_usuario = datos.get("id_usuario")
    id_sucursal = datos.get("id_sucursal_retiro")
    productos_solicitados = datos.get("productos")

    # 1. Validar los campos obligatorios.
    if id_usuario is None or id_sucursal is None:
        return {
            "status": "error",
            "message": "Faltan id_usuario o id_sucursal_retiro."
        }, 400

    if (
        isinstance(id_usuario, bool)
        or not isinstance(id_usuario, int)
        or id_usuario <= 0
    ):
        return {
            "status": "error",
            "message": "id_usuario debe ser un entero positivo."
        }, 400

    if (
        isinstance(id_sucursal, bool)
        or not isinstance(id_sucursal, int)
        or id_sucursal <= 0
    ):
        return {
            "status": "error",
            "message": "id_sucursal_retiro debe ser un entero positivo."
        }, 400

    if not isinstance(productos_solicitados, list) or not productos_solicitados:
        return {
            "status": "error",
            "message": "El pedido debe contener al menos un producto."
        }, 400

    # 2. Comprobar el horario operativo: 12:00 a 02:00.
    ahora = datetime.now()
    hora_actual = ahora.time()

    horario_permitido = (
        hora_actual >= datetime.strptime("12:00", "%H:%M").time()
        or hora_actual < datetime.strptime("02:00", "%H:%M").time()
    )

    if not horario_permitido:
        return {
            "status": "error",
            "message": "El Candy Bar está cerrado. Horario: 12:00 a 02:00."
        }, 400

    # 3. Comprobar que el usuario exista, esté activo y sea cliente.
    usuario = execute_query(
        """
        SELECT id_usuario
        FROM usuarios
        WHERE id_usuario = %s
          AND rol = 'CLIENTE'
          AND estado = 'ACTIVO'
        """,
        (id_usuario,),
        fetchone=True
    )

    if not usuario:
        return {
            "status": "error",
            "message": "El usuario no existe, no está activo o no es cliente."
        }, 404

    # 4. Comprobar que la sucursal exista y esté activa.
    sucursal = execute_query(
        """
        SELECT id_sucursal
        FROM sucursales
        WHERE id_sucursal = %s
          AND estado = 'ACTIVO'
        """,
        (id_sucursal,),
        fetchone=True
    )

    if not sucursal:
        return {
            "status": "error",
            "message": "La sucursal no existe o está inactiva."
        }, 404

    # 5. Validar los productos y las cantidades.
    cantidades_por_producto = {}
    total_unidades = 0

    for item in productos_solicitados:
        if not isinstance(item, dict):
            return {
                "status": "error",
                "message": "Cada producto debe ser un objeto JSON."
            }, 400

        id_producto = item.get("id_producto")
        cantidad = item.get("cantidad")

        if (
            isinstance(id_producto, bool)
            or not isinstance(id_producto, int)
            or id_producto <= 0
        ):
            return {
                "status": "error",
                "message": "Cada id_producto debe ser un entero positivo."
            }, 400

        if (
            isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
        ):
            return {
                "status": "error",
                "message": "Cada cantidad debe ser un entero positivo."
            }, 400

        cantidades_por_producto[id_producto] = (
            cantidades_por_producto.get(id_producto, 0) + cantidad
        )

        total_unidades += cantidad

    if total_unidades > 12:
        return {
            "status": "error",
            "message": "El pedido no puede superar las 12 unidades."
        }, 400

    # 6. Consultar en MySQL los productos activos.
    productos_bd = obtener_productos_activos_por_ids(
        list(cantidades_por_producto.keys())
    )

    productos_encontrados = {
        producto["id_producto"]: producto
        for producto in productos_bd
    }

    if len(productos_encontrados) != len(cantidades_por_producto):
        return {
            "status": "error",
            "message": "Uno o más productos no existen o están inactivos."
        }, 400

    # 7. Calcular los importes usando los precios de MySQL.
    detalles = []
    total = Decimal("0.00")

    for id_producto, cantidad in cantidades_por_producto.items():
        producto = productos_encontrados[id_producto]
        precio = Decimal(str(producto["precio_base"]))

        subtotal = precio * cantidad
        total += subtotal

        detalles.append({
            "id_producto": id_producto,
            "cantidad": cantidad,
            "precio_unitario": precio
        })

    # 8. Establecer un vencimiento inicial de 15 minutos.
    vencimiento = ahora + timedelta(minutes=15)

    # 9. Guardar la orden y sus detalles.
    try:
        id_orden = crear_orden_candybar(
            id_usuario=id_usuario,
            id_sucursal_retiro=id_sucursal,
            productos=detalles,
            total=total,
            vencimiento_bloqueo=vencimiento
        )
    except Exception:
        return {
            "status": "error",
            "message": "No se pudo crear el pedido."
        }, 500

    return {
        "status": "success",
        "message": "Pedido de Candy Bar creado correctamente.",
        "data": {
            "id_orden": id_orden,
            "tipo_orden": "CANDYBAR_EXPRESS",
            "id_funcion": None,
            "id_sucursal_retiro": id_sucursal,
            "productos": [
                {
                    "id_producto": detalle["id_producto"],
                    "cantidad": detalle["cantidad"],
                    "precio_unitario": str(detalle["precio_unitario"])
                }
                for detalle in detalles
            ],
            "total": str(total),
            "estado": "PENDIENTE",
            "vencimiento_bloqueo": vencimiento.isoformat(sep=" ")
        }
    }, 201