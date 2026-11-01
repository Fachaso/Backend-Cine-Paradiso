from datetime import datetime, timedelta, timezone
from decimal import Decimal

from flask import current_app, jsonify, request

from app.controllers.sucursal_controller import requiere_admin, respuesta_error
from app.services import funciones_service
from app.validators.funcion_validator import validar_datos_funcion


ZONA_HORARIA_ARGENTINA = timezone(timedelta(hours=-3))


def serializar_funcion(funcion):
    funcion_serializada = {}

    for campo, valor in funcion.items():
        if campo == "fecha_hora" and isinstance(valor, datetime):
            funcion_serializada[campo] = valor.replace(
                tzinfo=ZONA_HORARIA_ARGENTINA
            ).isoformat()
        elif isinstance(valor, Decimal):
            funcion_serializada[campo] = float(valor)
        else:
            funcion_serializada[campo] = valor

    return funcion_serializada


def listar_funciones():
    parametros = request.args
    filtros_permitidos = ("id_pelicula", "id_sucursal", "fecha")

    for nombre in parametros:
        if nombre not in filtros_permitidos:
            return respuesta_error(
                400,
                "DATOS_INVALIDOS",
                "Se recibieron parámetros de filtrado no válidos"
            )

        if len(parametros.getlist(nombre)) != 1:
            return respuesta_error(
                400,
                "DATOS_INVALIDOS",
                "Cada filtro debe recibirse una sola vez"
            )

    id_pelicula = None
    id_sucursal = None
    fecha = None

    valor_id_pelicula = parametros.get("id_pelicula")
    if valor_id_pelicula is not None:
        try:
            id_pelicula = int(valor_id_pelicula)
            if id_pelicula <= 0 or not valor_id_pelicula.isdigit():
                return respuesta_error(
                    400,
                    "DATOS_INVALIDOS",
                    "El id de película debe ser un entero positivo"
                )
        except (TypeError, ValueError):
            return respuesta_error(
                400,
                "DATOS_INVALIDOS",
                "El id de película debe ser un entero positivo"
            )

    valor_id_sucursal = parametros.get("id_sucursal")
    if valor_id_sucursal is not None:
        try:
            id_sucursal = int(valor_id_sucursal)
            if id_sucursal <= 0 or not valor_id_sucursal.isdigit():
                return respuesta_error(
                    400,
                    "DATOS_INVALIDOS",
                    "El id de sucursal debe ser un entero positivo"
                )
        except (TypeError, ValueError):
            return respuesta_error(
                400,
                "DATOS_INVALIDOS",
                "El id de sucursal debe ser un entero positivo"
            )

    valor_fecha = parametros.get("fecha")
    if valor_fecha is not None:
        try:
            fecha_convertida = datetime.strptime(valor_fecha, "%Y-%m-%d")
            if fecha_convertida.strftime("%Y-%m-%d") != valor_fecha:
                return respuesta_error(
                    400,
                    "DATOS_INVALIDOS",
                    "La fecha debe tener formato YYYY-MM-DD válido"
                )
            fecha = valor_fecha
        except (TypeError, ValueError):
            return respuesta_error(
                400,
                "DATOS_INVALIDOS",
                "La fecha debe tener formato YYYY-MM-DD válido"
            )

    try:
        funciones, error, codigo_http = funciones_service.listar_funciones(
            id_pelicula, id_sucursal, fecha
        )

        if error is not None:
            return respuesta_error(
                codigo_http,
                "ERROR_CONSULTA",
                error
            )

        funciones_serializadas = [
            serializar_funcion(funcion) for funcion in funciones
        ]

        return jsonify({
            "status": "success",
            "data": funciones_serializadas
        }), codigo_http

    except Exception:
        current_app.logger.exception(
            "Error al obtener las funciones"
        )

        return respuesta_error(
            500,
            "ERROR_INTERNO",
            "No fue posible obtener las funciones"
        )


def obtener_funcion_por_id(id_funcion):
    if isinstance(id_funcion, bool) or not isinstance(id_funcion, int) or id_funcion <= 0:
        return respuesta_error(
            400,
            "DATOS_INVALIDOS",
            "El id de función debe ser un entero positivo"
        )

    try:
        funcion, error, codigo_http = funciones_service.obtener_funcion_por_id(
            id_funcion
        )

        if error is not None:
            return respuesta_error(
                codigo_http,
                "FUNCION_NO_ENCONTRADA",
                error
            )

        return jsonify({
            "status": "success",
            "data": serializar_funcion(funcion)
        }), codigo_http

    except Exception:
        current_app.logger.exception(
            "Error al obtener la función %s",
            id_funcion
        )

        return respuesta_error(
            500,
            "ERROR_INTERNO",
            "No fue posible obtener la función"
        )


@requiere_admin
def crear_funcion():
    datos_funcion, mensaje = validar_datos_funcion(
        request.get_json(silent=True)
    )

    if mensaje is not None:
        return respuesta_error(
            400,
            "DATOS_INVALIDOS",
            mensaje
        )

    try:
        funcion, error, codigo_http = funciones_service.crear_funcion(
            datos_funcion
        )

        if error == "La película no existe":
            return respuesta_error(
                404,
                "PELICULA_NO_ENCONTRADA",
                error
            )

        if error == "La sala no existe":
            return respuesta_error(
                404,
                "SALA_NO_ENCONTRADA",
                error
            )

        if codigo_http == 409:
            return respuesta_error(
                409,
                "SUPERPOSICION_HORARIA",
                error
            )

        if error is not None:
            return respuesta_error(
                codigo_http,
                "ERROR_CREAR_FUNCION",
                error
            )

        return jsonify({
            "status": "success",
            "data": serializar_funcion(funcion)
        }), codigo_http

    except Exception:
        current_app.logger.exception(
            "Error al crear la función"
        )

        return respuesta_error(
            500,
            "ERROR_INTERNO",
            "No fue posible crear la función"
        )