from flask import current_app, jsonify, request, session

from app.utils.auth import respuesta_error
from app.services import resena_service


CODIGOS_HTTP_CREAR = {
    "PELICULA_NO_ENCONTRADA": 404,
    "DATOS_INVALIDOS": 400,
    "RESENA_NO_HABILITADA": 403,
    "RESENA_DUPLICADA": 409,
}


def _obtener_id_usuario():
    id_usuario = session.get("id_usuario")
    if id_usuario is None:
        return None, respuesta_error(
            "NO_AUTENTICADO", "Debés iniciar sesión para reseñar una película", 401
        )
    return id_usuario, None


def listar_resenas(id_pelicula):
    try:
        resenas, codigo = resena_service.listar_resenas(id_pelicula)

        if codigo == "PELICULA_NO_ENCONTRADA":
            return respuesta_error("PELICULA_NO_ENCONTRADA", "Película no encontrada", 404)

        return jsonify({"status": "success", "data": resenas}), 200
    except Exception:
        current_app.logger.exception("Error al listar reseñas")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)


def crear_resena(id_pelicula):
    try:
        id_usuario, error = _obtener_id_usuario()
        if error:
            return error

        datos = request.get_json(silent=True)
        resena, codigo, mensaje = resena_service.crear_resena(id_usuario, id_pelicula, datos)

        if codigo in CODIGOS_HTTP_CREAR:
            return respuesta_error(codigo, mensaje, CODIGOS_HTTP_CREAR[codigo])

        return jsonify({"status": "success", "data": resena}), 201
    except Exception:
        current_app.logger.exception("Error al crear reseña")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)