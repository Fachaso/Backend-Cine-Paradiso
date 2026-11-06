from flask import current_app, jsonify, request, session

from app.services import auth_service
from app.utils.auth import respuesta_error
from app.validators.usuario_validator import (
    validar_datos_login,
    validar_datos_registro,
)


def registro():
    datos = request.get_json(silent=True) or {}
    es_valido, codigo_err, msg_err, limpiados = validar_datos_registro(datos)

    if not es_valido:
        return respuesta_error(codigo_err, msg_err, 400)

    nombre, email, password = limpiados

    try:
        data, code, msg, status_code = auth_service.registrar_nuevo_usuario(
            nombre, email, password
        )

        if code:
            return respuesta_error(code, msg, status_code)

        return jsonify({"status": "success", "data": data}), status_code

    except Exception:
        current_app.logger.exception("Error al registrar usuario")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)


def login():
    datos = request.get_json(silent=True) or {}
    es_valido, codigo_err, msg_err, limpiados = validar_datos_login(datos)

    if not es_valido:
        return respuesta_error(codigo_err, msg_err, 400)

    email, password = limpiados

    try:
        data, code, msg, status_code = auth_service.autenticar_usuario(email, password)

        if code:
            return respuesta_error(code, msg, status_code)

        return jsonify({"status": "success", "data": data}), status_code

    except Exception:
        current_app.logger.exception("Error al iniciar sesi贸n")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)


def logout():
    if not session.get("id_usuario"):
        return respuesta_error("NO_AUTENTICADO", "No hay una sesi贸n activa", 401)

    auth_service.cerrar_sesion_activa()
    return jsonify({"status": "success", "data": {"message": "Sesi贸n cerrada"}}), 200


def me():
    id_usuario = session.get("id_usuario")
    if not id_usuario:
        return respuesta_error("NO_AUTENTICADO", "No hay una sesi贸n activa", 401)

    try:
        data, code, msg, status_code = auth_service.obtener_usuario_actual(id_usuario)

        if code:
            return respuesta_error(code, msg, status_code)

        return jsonify({"status": "success", "data": data}), status_code

    except Exception:
        current_app.logger.exception("Error al consultar usuario autenticado")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)