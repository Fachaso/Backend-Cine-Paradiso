
from datetime import date, datetime
from decimal import Decimal

from flask import current_app, jsonify, request, session

from app.utils.auth import respuesta_error
from app.services import compras_service
from app.validators.compra_validator import (
    validar_solicitud_compra,
    validar_solicitud_actualizacion_compra,
)


def _serializar(valor):
    if isinstance(valor, dict):
        return {clave: _serializar(dato) for clave, dato in valor.items()}
    if isinstance(valor, list):
        return [_serializar(dato) for dato in valor]
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    return valor


def _obtener_id_cliente():
    id_usuario = session.get("id_usuario")
    if id_usuario is None:
        return None, respuesta_error(
            "NO_AUTENTICADO", "Debés iniciar sesión para realizar esta operación", 401
        )
    if session.get("rol") != "CLIENTE":
        return None, respuesta_error(
            "ACCESO_DENEGADO", "La operación está disponible para clientes", 403
        )
    return id_usuario, None


def _responder_error_compra(error, codigo_http):
    codigo = error.get("code", error.get("codigo", "ERROR_COMPRA"))
    mensaje = error.get(
        "message", error.get("mensaje", "No fue posible procesar la compra")
    )
    return respuesta_error(codigo, mensaje, codigo_http)


def _armar_detalle_compra(compra):
    cabecera = {
        clave: valor for clave, valor in compra.items()
        if clave not in ("entradas", "servicios")
    }
    return {
        "compra": cabecera,
        "entradas": compra.get("entradas", []),
        "servicios": compra.get("servicios", []),
    }


def crear_compra():
    id_usuario, respuesta = _obtener_id_cliente()
    if respuesta is not None:
        return respuesta
    datos, mensaje = validar_solicitud_compra(request.get_json(silent=True))
    if mensaje:
        return respuesta_error("DATOS_INVALIDOS", mensaje, 400)
    try:
        compra, error, status = compras_service.crear_compra_pendiente(id_usuario, datos)
        if error is not None:
            return _responder_error_compra(error, status)
        return jsonify({"status": "success", "data": _serializar(compra)}), status
    except Exception:
        current_app.logger.exception("Error al iniciar la compra")
        return respuesta_error("ERROR_INTERNO", "No fue posible iniciar la compra", 500)


def confirmar_compra(id_compra):
    id_usuario, respuesta = _obtener_id_cliente()
    if respuesta is not None:
        return respuesta
    if id_compra <= 0:
        return respuesta_error("DATOS_INVALIDOS", "El id de compra debe ser positivo", 400)
    datos, mensaje = validar_solicitud_actualizacion_compra(
        request.get_json(silent=True)
    )
    if mensaje:
        return respuesta_error("DATOS_INVALIDOS", mensaje, 400)
    try:
        if datos["estado_compra"] == "CONFIRMADA":
            _, error, status = compras_service.confirmar_compra(
                id_compra, id_usuario, datos
            )
        else:
            _, error, status = compras_service.cancelar_compra(
                id_compra, id_usuario
            )
        if error is not None:
            return _responder_error_compra(error, status)
        compra, error, status = compras_service.obtener_compra(id_compra, id_usuario)
        if error is not None:
            return _responder_error_compra(error, status)
        cabecera = {
            k: v for k, v in compra.items() if k not in ("entradas", "servicios")
        }
        return jsonify({
            "status": "success",
            "data": {
                "compra": _serializar(cabecera),
                "entradas": _serializar(compra.get("entradas", [])),
                "servicios": _serializar(compra.get("servicios", [])),
            }
        }), status
    except Exception:
        current_app.logger.exception("Error al actualizar la compra %s", id_compra)
        return respuesta_error(
            "ERROR_INTERNO", "No fue posible actualizar la compra", 500
        )


def obtener_compra(id_compra):
    id_usuario, respuesta = _obtener_id_cliente()
    if respuesta is not None:
        return respuesta
    if id_compra <= 0:
        return respuesta_error("DATOS_INVALIDOS", "El id de compra debe ser positivo", 400)
    try:
        compra, error, status = compras_service.obtener_compra(id_compra, id_usuario)
        if error is not None:
            return _responder_error_compra(error, status)
        cabecera = {
            k: v for k, v in compra.items() if k not in ("entradas", "servicios")
        }
        return jsonify({
            "status": "success",
            "data": {
                "compra": _serializar(cabecera),
                "entradas": _serializar(compra.get("entradas", [])),
                "servicios": _serializar(compra.get("servicios", [])),
            }
        }), status
    except Exception:
        current_app.logger.exception("Error al consultar la compra %s", id_compra)
        return respuesta_error(
            "ERROR_INTERNO", "No fue posible consultar la compra", 500
        )
