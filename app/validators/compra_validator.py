CAMPOS_CREAR = ("id_funcion", "asientos_ids", "servicios")
CAMPOS_SERVICIO_PERMITIDOS = ("id_servicio", "cantidad")
CANTIDAD_MAXIMA_SERVICIO = 10


def _es_entero_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


def _validar_servicios(servicios):
    if not isinstance(servicios, list):
        return None, "servicios debe ser una lista"

    cantidades = {}
    for indice, servicio in enumerate(servicios):
        if not isinstance(servicio, dict):
            return None, f"El servicio en la posición {indice} debe ser un objeto"
        if any(campo not in CAMPOS_SERVICIO_PERMITIDOS for campo in servicio):
            return None, f"Hay un campo no válido en el servicio {indice}"

        id_servicio = servicio.get("id_servicio")
        cantidad = servicio.get("cantidad")
        if not _es_entero_positivo(id_servicio):
            return None, "id_servicio debe ser un entero positivo"
        if (
            isinstance(cantidad, bool) or not isinstance(cantidad, int)
            or cantidad < 0 or cantidad > CANTIDAD_MAXIMA_SERVICIO
        ):
            return None, "La cantidad de cada servicio debe ser de 0 a 10"

        cantidades[id_servicio] = cantidades.get(id_servicio, 0) + cantidad
        if cantidades[id_servicio] > CANTIDAD_MAXIMA_SERVICIO:
            return None, (
                f"La cantidad total del servicio {id_servicio} no puede superar 10"
            )

    normalizados = [
        {"id_servicio": id_servicio, "cantidad": cantidad}
        for id_servicio, cantidad in cantidades.items() if cantidad > 0
    ]
    return normalizados, None


def validar_solicitud_compra(datos):
    if not isinstance(datos, dict):
        return None, "El cuerpo de la solicitud debe ser un objeto JSON"
    for campo in datos:
        if campo not in CAMPOS_CREAR:
            return None, f"El campo {campo} no es válido"

    id_funcion = datos.get("id_funcion")
    if not _es_entero_positivo(id_funcion):
        return None, "id_funcion debe ser un entero positivo"

    asientos = datos.get("asientos_ids")
    if not isinstance(asientos, list) or not asientos:
        return None, "Debe enviar una lista no vacía de asientos_ids"
    if any(not _es_entero_positivo(id_asiento) for id_asiento in asientos):
        return None, "Cada asiento_id debe ser un entero positivo"
    if len(asientos) != len(set(asientos)):
        return None, "No se permiten asientos_ids repetidos"

    servicios, mensaje = _validar_servicios(datos.get("servicios", []))
    if mensaje:
        return None, mensaje

    return {
        "id_funcion": id_funcion,
        "asientos_ids": list(asientos),
        "servicios": servicios,
    }, None


def validar_solicitud_actualizacion_compra(datos):
    if not isinstance(datos, dict):
        return None, "El cuerpo de la solicitud debe ser un objeto JSON"
    if datos == {"estado_qr": "CANCELADO"} or datos == {"estado_compra": "CANCELADA"}:
        return {"estado_compra": "CANCELADA"}, None
    return None, 'Para cancelar solo debe enviar {"estado_qr":"CANCELADO"}'
