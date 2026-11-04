from app.repositories import control_acceso_repository


def validar_qr(codigo_qr, id_funcion):
    qr = control_acceso_repository.obtener_qr(codigo_qr)
    if qr is None:
        return None, "QR_NO_ENCONTRADO"
    if qr["estado_qr"] != "PENDIENTE":
        return None, "QR_NO_VALIDO"
    if not control_acceso_repository.qr_pertenece_a_funcion(codigo_qr, id_funcion):
        return None, "QR_FUNCION_INCORRECTA"

    control_acceso_repository.marcar_qr_usado(codigo_qr)
    return {"codigo_qr": codigo_qr, "estado_qr": "USADO"}, None

