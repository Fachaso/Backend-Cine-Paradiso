
from functools import wraps

from flask import current_app, jsonify, request, session
from mysql.connector import Error

from app.services import sucursal_service
from app.validators.sucursal_validator import (
    obtener_rol_de_sesion,
    validar_datos_sala,
    validar_id_sucursal,
)

def respuesta_error(codigo_http, codigo, mensaje):
    return jsonify({
        "status": "error",
        "code": codigo,
        "message": mensaje
    }), codigo_http

def requiere_admin(funcion):

    @wraps(funcion)
    def funcion_protegida(*args, **kwargs):
        rol = obtener_rol_de_sesion(session)

        if rol is None:
            return respuesta_error(
                401,
                "NO_AUTENTICADO",
                "Se requiere autenticación"
            )

        if rol != "ADMIN":
            return respuesta_error(
                403,
                "PERMISOS_INSUFICIENTES",
                "Se requiere rol ADMIN"
            )

        return funcion(*args, **kwargs)

    return funcion_protegida

def listar_sucursales():

    try:
        sucursales = sucursal_service.listar_sucursales()

        return jsonify({
            "status": "success",
            "data": sucursales
        }), 200

    except Exception:
        current_app.logger.exception(
            "Error al obtener las sucursales"
        )

        return respuesta_error(
            500,
            "ERROR_INTERNO",
            "No fue posible obtener las sucursales"
        )

def listar_salas(id_sucursal):

    es_valido, mensaje = validar_id_sucursal(id_sucursal)

    if not es_valido:
        return respuesta_error(
            400,
            "ID_INVALIDO",
            mensaje
        )

    try:
        salas, error = sucursal_service.obtener_salas_de_sucursal(
            id_sucursal
        )

        if error == "SUCURSAL_NO_ENCONTRADA":
            return respuesta_error(
                404,
                "SUCURSAL_NO_ENCONTRADA",
                "La sucursal no existe"
            )

        return jsonify({
            "status": "success",
            "data": salas
        }), 200

    except Exception:
        current_app.logger.exception(
            "Error al obtener las salas de la sucursal %s",
            id_sucursal
        )

        return respuesta_error(
            500,
            "ERROR_INTERNO",
            "No fue posible obtener las salas"
        )

@requiere_admin
def crear_sala(id_sucursal):

    es_valido, mensaje = validar_id_sucursal(id_sucursal)

    if not es_valido:
        return respuesta_error(
            400,
            "ID_INVALIDO",
            mensaje
        )

    datos_sala, mensaje = validar_datos_sala(
        request.get_json(silent=True)
    )

    if mensaje is not None:
        return respuesta_error(
            400,
            "DATOS_INVALIDOS",
            mensaje
        )

    try:
        sala, error = sucursal_service.crear_sala(
            id_sucursal,
            datos_sala
        )

        if error == "SUCURSAL_NO_ENCONTRADA":
            return respuesta_error(
                404,
                "SUCURSAL_NO_ENCONTRADA",
                "La sucursal no existe"
            )

        if error == "SALA_DUPLICADA":
            return respuesta_error(
                409,
                "SALA_DUPLICADA",
                "Ya existe una sala con ese nombre en la sucursal"
            )

        return jsonify({
            "status": "success",
            "data": sala
        }), 201

    except Error as error:
        current_app.logger.exception(
            "Error de MySQL al crear la sala"
        )

        if error.errno == 1062:
            return respuesta_error(
                409,
                "SALA_DUPLICADA",
                "Ya existe una sala con ese nombre en la sucursal"
            )

        return respuesta_error(
            500,
            "ERROR_INTERNO",
            "No fue posible crear la sala"
        )

    except Exception:
        current_app.logger.exception(
            "Error inesperado al crear la sala"
        )

        return respuesta_error(
            500,
            "ERROR_INTERNO",
            "No fue posible crear la sala"
        )