from flask import jsonify, session

"""Funciones auxiliares de autenticación, sin consultas a la base de datos."""

def respuesta_error(codigo, mensaje, estado_http):
    return jsonify({"status": "error", "code": codigo, "message": mensaje}), estado_http


def datos_publicos_usuario(usuario):
    return {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "rol": usuario["rol"],
    }


def iniciar_sesion(usuario):
    session.clear()
    session["id_usuario"] = usuario["id_usuario"]
    session["rol"] = usuario["rol"]


def cerrar_sesion():
    session.clear()
