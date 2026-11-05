from flask import Response, current_app, jsonify, request, session
from app.services.estadisticas_service import (
    generar_reporte_pdf_service,
    obtener_cancelaciones_service,
    obtener_franjas_horarias_service,
    obtener_ocupacion_service,
    obtener_ventas_por_genero_service,
)

def verificar_acceso_admin():
    """
    Verifica que la sesión activa corresponda a un usuario autenticado con rol ADMIN.
    """
    id_usuario = session.get("id_usuario")
    if not id_usuario:
        return jsonify({
            "status": "error",
            "code": "NO_AUTENTICADO",
            "message": "No autorizado (Requiere autenticación)"
        }), 401

    rol = session.get("rol")
    if rol != "ADMIN":
        return jsonify({
            "status": "error",
            "code": "ACCESO_DENEGADO",
            "message": "Acceso prohibido (Permisos insuficientes)"
        }), 403

    return None


def obtener_ocupacion_controller():
    error_auth = verificar_acceso_admin()
    if error_auth:
        return error_auth

    try:
        id_funcion_raw = request.args.get("id_funcion")
        id_pelicula_raw = request.args.get("id_pelicula")

        id_funcion = None
        if id_funcion_raw is not None and id_funcion_raw != "":
            try:
                id_funcion = int(id_funcion_raw)
                if id_funcion <= 0:
                    raise ValueError()
            except ValueError:
                return jsonify({
                    "status": "error",
                    "code": "SOLICITUD_INVALIDA",
                    "message": "El parámetro 'id_funcion' debe ser un número entero positivo"
                }), 400

        id_pelicula = None
        if id_pelicula_raw is not None and id_pelicula_raw != "":
            try:
                id_pelicula = int(id_pelicula_raw)
                if id_pelicula <= 0:
                    raise ValueError()
            except ValueError:
                return jsonify({
                    "status": "error",
                    "code": "SOLICITUD_INVALIDA",
                    "message": "El parámetro 'id_pelicula' debe ser un número entero positivo"
                }), 400

        data, error, status_code = obtener_ocupacion_service(
            id_funcion=id_funcion,
            id_pelicula=id_pelicula
        )
        if error:
            return jsonify({"status": "error", "code": "ERROR_PROCESAMIENTO", "message": error}), status_code

        return jsonify({"status": "success", "data": data}), status_code

    except Exception:
        current_app.logger.exception("Error en obtener_ocupacion_controller")
        return jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno del servidor"
        }), 500


def obtener_ventas_por_genero_controller():
    error_auth = verificar_acceso_admin()
    if error_auth:
        return error_auth

    try:
        data, error, status_code = obtener_ventas_por_genero_service()
        if error:
            return jsonify({"status": "error", "code": "ERROR_PROCESAMIENTO", "message": error}), status_code

        return jsonify({"status": "success", "data": data}), status_code

    except Exception:
        current_app.logger.exception("Error en obtener_ventas_por_genero_controller")
        return jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno del servidor"
        }), 500


def obtener_franjas_horarias_controller():
    error_auth = verificar_acceso_admin()
    if error_auth:
        return error_auth

    try:
        data, error, status_code = obtener_franjas_horarias_service()
        if error:
            return jsonify({"status": "error", "code": "ERROR_PROCESAMIENTO", "message": error}), status_code

        return jsonify({"status": "success", "data": data}), status_code

    except Exception:
        current_app.logger.exception("Error en obtener_franjas_horarias_controller")
        return jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno del servidor"
        }), 500


def obtener_cancelaciones_controller():
    error_auth = verificar_acceso_admin()
    if error_auth:
        return error_auth

    try:
        data, error, status_code = obtener_cancelaciones_service()
        if error:
            return jsonify({"status": "error", "code": "ERROR_PROCESAMIENTO", "message": error}), status_code

        return jsonify({"status": "success", "data": data}), status_code

    except Exception:
        current_app.logger.exception("Error en obtener_cancelaciones_controller")
        return jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno del servidor"
        }), 500
        

def generar_reporte_pdf_controller():
    error_auth = verificar_acceso_admin()
    if error_auth:
        return error_auth

    try:
        pdf_buffer, error, status_code = generar_reporte_pdf_service()
        if error:
            return jsonify({"status": "error", "code": "ERROR_REPORTE", "message": error}), status_code

        return Response(
            pdf_buffer.getvalue(),
            mimetype="application/pdf",
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment; filename=reporte_estadisticas.pdf"
            },
            status=200
        )

    except Exception:
        current_app.logger.exception("Error al generar el PDF de estadísticas")
        return jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": "Error interno al generar el reporte PDF"
        }), 500
