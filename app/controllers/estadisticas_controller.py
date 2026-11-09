from flask import Response, current_app, jsonify, request

from app.controllers.sucursal_controller import requiere_admin
from app.services.estadisticas_service import (
    generar_reporte_pdf_service,
    obtener_cancelaciones_service,
    obtener_franjas_horarias_service,
    obtener_ocupacion_service,
    obtener_ventas_por_genero_service,
)


@requiere_admin
def obtener_ocupacion_controller():
    respuesta = None
    codigo_http = 200

    try:
        id_funcion_raw = request.args.get("id_funcion")
        id_pelicula_raw = request.args.get("id_pelicula")

        id_funcion = None
        id_pelicula = None
        mensaje_error = None

        if id_funcion_raw is not None and id_funcion_raw != "":
            try:
                id_funcion = int(id_funcion_raw)

                if id_funcion <= 0:
                    raise ValueError()

            except ValueError:
                mensaje_error = (
                    "El parámetro 'id_funcion' debe ser "
                    "un número entero positivo"
                )

        if mensaje_error is None and id_pelicula_raw is not None and id_pelicula_raw != "":
            try:
                id_pelicula = int(id_pelicula_raw)

                if id_pelicula <= 0:
                    raise ValueError()

            except ValueError:
                mensaje_error = (
                    "El parámetro 'id_pelicula' debe ser "
                    "un número entero positivo"
                )

        if mensaje_error is not None:
            respuesta = jsonify({
                "status": "error",
                "code": "SOLICITUD_INVALIDA",
                "message": mensaje_error
            })
            codigo_http = 400

        else:
            data, error, codigo_http = obtener_ocupacion_service(
                id_funcion=id_funcion,
                id_pelicula=id_pelicula
            )

            if error is not None:
                respuesta = jsonify({
                    "status": "error",
                    "code": "ERROR_PROCESAMIENTO",
                    "message": error
                })

            else:
                respuesta = jsonify({
                    "status": "success",
                    "data": data
                })

    except Exception:
        current_app.logger.exception(
            "Error en obtener_ocupacion_controller"
        )

        respuesta = jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno del servidor"
        })
        codigo_http = 500

    return respuesta, codigo_http


@requiere_admin
def obtener_ventas_por_genero_controller():
    respuesta = None
    codigo_http = 200

    try:
        data, error, codigo_http = obtener_ventas_por_genero_service()

        if error is not None:
            respuesta = jsonify({
                "status": "error",
                "code": "ERROR_PROCESAMIENTO",
                "message": error
            })

        else:
            respuesta = jsonify({
                "status": "success",
                "data": data
            })

    except Exception:
        current_app.logger.exception(
            "Error en obtener_ventas_por_genero_controller"
        )

        respuesta = jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno del servidor"
        })
        codigo_http = 500

    return respuesta, codigo_http


@requiere_admin
def obtener_franjas_horarias_controller():
    respuesta = None
    codigo_http = 200

    try:
        data, error, codigo_http = obtener_franjas_horarias_service()

        if error is not None:
            respuesta = jsonify({
                "status": "error",
                "code": "ERROR_PROCESAMIENTO",
                "message": error
            })

        else:
            respuesta = jsonify({
                "status": "success",
                "data": data
            })

    except Exception:
        current_app.logger.exception(
            "Error en obtener_franjas_horarias_controller"
        )

        respuesta = jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno del servidor"
        })
        codigo_http = 500

    return respuesta, codigo_http


@requiere_admin
def obtener_cancelaciones_controller():
    respuesta = None
    codigo_http = 200

    try:
        data, error, codigo_http = obtener_cancelaciones_service()

        if error is not None:
            respuesta = jsonify({
                "status": "error",
                "code": "ERROR_PROCESAMIENTO",
                "message": error
            })

        else:
            respuesta = jsonify({
                "status": "success",
                "data": data
            })

    except Exception:
        current_app.logger.exception(
            "Error en obtener_cancelaciones_controller"
        )

        respuesta = jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno del servidor"
        })
        codigo_http = 500

    return respuesta, codigo_http


@requiere_admin
def generar_reporte_pdf_controller():
    respuesta = None
    codigo_http = 200

    try:
        pdf_buffer, error, codigo_http = generar_reporte_pdf_service()

        if error is not None:
            respuesta = jsonify({
                "status": "error",
                "code": "ERROR_REPORTE",
                "message": error
            })

        else:
            respuesta = Response(
                pdf_buffer.getvalue(),
                mimetype="application/pdf",
                headers={
                    "Content-Disposition": (
                        "attachment; filename=reporte_estadisticas.pdf"
                    )
                }
            )

    except Exception:
        current_app.logger.exception(
            "Error al generar el PDF de estadísticas"
        )

        respuesta = jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno al generar el reporte PDF"
        })
        codigo_http = 500

    return respuesta, codigo_http