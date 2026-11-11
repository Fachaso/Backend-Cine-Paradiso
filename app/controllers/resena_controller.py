from flask import current_app, jsonify

from app.utils.auth import respuesta_error
from app.services import resena_service


def listar_resenas(id_pelicula):
    try:
        resenas, codigo = resena_service.listar_resenas(id_pelicula)

        if codigo == "PELICULA_NO_ENCONTRADA":
            return respuesta_error("PELICULA_NO_ENCONTRADA", "Película no encontrada", 404)

        return jsonify({"status": "success", "data": resenas}), 200
    except Exception:
        current_app.logger.exception("Error al listar reseñas")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)