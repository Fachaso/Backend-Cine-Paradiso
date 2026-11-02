from flask import current_app, jsonify

from app.auth import respuesta_error
from app.services import servicio_service


def listar_servicios():
    try:
        servicios = servicio_service.listar_servicios()

        return jsonify({
            "status": "success",
            "data": servicios
        }), 200

    except Exception:
        current_app.logger.exception("Error al obtener los servicios")

        return respuesta_error(
            "ERROR_INTERNO",
            "No fue posible obtener los servicios",
            500
        )


def obtener_servicio(id_servicio):
    try:
        servicio, error = servicio_service.obtener_servicio(id_servicio)

        if error == "SERVICIO_NO_ENCONTRADO":
            return respuesta_error(
                "SERVICIO_NO_ENCONTRADO",
                "El servicio no existe",
                404
            )

        return jsonify({
            "status": "success",
            "data": servicio
        }), 200

    except Exception:
        current_app.logger.exception(
            "Error al obtener el servicio %s", id_servicio
        )

        return respuesta_error(
            "ERROR_INTERNO",
            "No fue posible obtener el servicio",
            500
        )
