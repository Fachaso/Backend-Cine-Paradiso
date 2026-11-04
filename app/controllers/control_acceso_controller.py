from flask import current_app, jsonify, request

from app.controllers.sucursal_controller import requiere_admin, respuesta_error
from app.services import control_acceso_service

ERRORES_QR = {
    "QR_NO_ENCONTRADO": (404, "El código QR no existe"),
    "QR_NO_VALIDO": (409, "El código QR ya fue usado o está cancelado"),
    "QR_FUNCION_INCORRECTA": (409, "El código QR no corresponde a esta función"),
}


@requiere_admin
def validar_qr_ingreso(codigo_qr):
    cuerpo = request.get_json(silent=True)
    id_funcion = cuerpo.get("id_funcion") if isinstance(cuerpo, dict) else None

    if not isinstance(id_funcion, int) or isinstance(id_funcion, bool) or id_funcion < 1:
        return respuesta_error(400, "DATOS_INVALIDOS", "id_funcion debe ser un entero positivo")

    try:
        dato, error = control_acceso_service.validar_qr(codigo_qr, id_funcion)

        if error is not None:
            estado_http, mensaje = ERRORES_QR[error]
            return respuesta_error(estado_http, error, mensaje)

        return jsonify({"status": "success", "data": dato}), 200
    except Exception:
        current_app.logger.exception("Error al validar el código QR")
        return respuesta_error(500, "ERROR_INTERNO", "No fue posible validar el código QR")
