from flask import current_app, jsonify, request

from app.utils.auth import respuesta_error
from app.controllers.sucursal_controller import requiere_admin
from app.services import control_acceso_service
from app.validators.control_acceso_validator import validar_solicitud_usar_qr


@requiere_admin
def usar_codigo_qr(codigo_qr):
    id_funcion, mensaje = validar_solicitud_usar_qr(request.get_json(silent=True))
    if mensaje:
        return respuesta_error("DATOS_INVALIDOS", mensaje, 400)

    try:
        resultado, error, status = control_acceso_service.usar_codigo_qr(
            codigo_qr, id_funcion
        )
        if error is not None:
            return respuesta_error(error["code"], error["message"], status)
        return jsonify({"status": "success", "data": resultado}), status
    except Exception:
        current_app.logger.exception("Error al validar el código QR %s", codigo_qr)
        return respuesta_error("ERROR_INTERNO", "No fue posible validar el código QR", 500)