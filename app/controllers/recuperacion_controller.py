from flask import current_app, jsonify, request

from app.services import recuperacion_service
from app.utils.auth import respuesta_error
from app.validators.recuperacion_validator import (
    validar_restablecimiento_password,
    validar_solicitud_recuperacion,
)


def solicitar_recuperacion():
    datos = request.get_json(silent=True) or {}
    es_valido, codigo_err, msg_err, limpiados = validar_solicitud_recuperacion(datos)

    if not es_valido:
        return respuesta_error(codigo_err, msg_err, 400)

    email, frontend_url = limpiados

    try:
        data, code, msg, status_code = recuperacion_service.solicitar_recuperacion_password(
            email, frontend_url
        )

        if code:
            return respuesta_error(code, msg, status_code)

        return jsonify({"status": "success", "data": data}), status_code

    except Exception:
        current_app.logger.exception("Error al solicitar recuperacion de contraseña")
        return respuesta_error(
            "ERROR_INTERNO", "No se pudo enviar el correo de recuperación", 500
        )


def restablecer_password():
    datos = request.get_json(silent=True) or {}
    es_valido, codigo_err, msg_err, limpiados = validar_restablecimiento_password(datos)

    if not es_valido:
        return respuesta_error(codigo_err, msg_err, 400)

    token, password = limpiados

    try:
        data, code, msg, status_code = recuperacion_service.restablecer_password(
            token, password
        )

        if code:
            return respuesta_error(code, msg, status_code)

        return jsonify({"status": "success", "data": data}), status_code

    except Exception:
        current_app.logger.exception("Error al restablecer contraseña")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)