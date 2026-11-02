from flask import current_app, jsonify, request

from app.auth import respuesta_error
from app.services import servicio_service
from app.controllers.sucursal_controller import requiere_admin


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


@requiere_admin
def crear_servicio():
    try:
        datos = request.get_json(silent=True)
        servicio, codigo, mensaje = servicio_service.crear_servicio(datos)

        if codigo == "DATOS_INVALIDOS":
            return respuesta_error("DATOS_INVALIDOS", mensaje, 400)
        if codigo == "SERVICIO_DUPLICADO":
            return respuesta_error("SERVICIO_DUPLICADO", mensaje, 409)

        return jsonify({"status": "success", "data": servicio}), 201
    except Exception:
        current_app.logger.exception("Error al crear servicio")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)


@requiere_admin
def actualizar_servicio(id_servicio):
    try:
        datos = request.get_json(silent=True)
        servicio, codigo, mensaje = servicio_service.actualizar_servicio(id_servicio, datos)

        if codigo == "SERVICIO_NO_ENCONTRADO":
            return respuesta_error("SERVICIO_NO_ENCONTRADO", mensaje, 404)
        if codigo == "DATOS_INVALIDOS":
            return respuesta_error("DATOS_INVALIDOS", mensaje, 400)
        if codigo == "SERVICIO_DUPLICADO":
            return respuesta_error("SERVICIO_DUPLICADO", mensaje, 409)

        return jsonify({"status": "success", "data": servicio}), 200
    except Exception:
        current_app.logger.exception("Error al actualizar servicio")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)


@requiere_admin
def eliminar_servicio(id_servicio):
    try:
        codigo, mensaje = servicio_service.eliminar_servicio(id_servicio)

        if codigo == "SERVICIO_NO_ENCONTRADO":
            return respuesta_error("SERVICIO_NO_ENCONTRADO", mensaje, 404)
        if codigo == "SERVICIO_EN_USO":
            return respuesta_error("SERVICIO_EN_USO", mensaje, 409)

        return "", 204
    except Exception:
        current_app.logger.exception("Error al eliminar servicio")
        return respuesta_error("ERROR_INTERNO", "Error interno del servidor", 500)