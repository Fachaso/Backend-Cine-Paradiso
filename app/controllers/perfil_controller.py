from flask import current_app, jsonify, session

from app.auth import respuesta_error
from app.services import perfil_service


def consultar_perfil():
    id_usuario = session.get("id_usuario")
    if not id_usuario:
        return respuesta_error("NO_AUTENTICADO", "No hay una sesión activa", 401)

    try:
        datos, error = perfil_service.obtener_perfil(id_usuario)
        if error:
            return respuesta_error("NO_AUTENTICADO", "La sesión ya no es válida", 401)
        return jsonify({"status": "success", "data": datos}), 200
    except Exception:
        current_app.logger.exception("Error al consultar el perfil")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)