from werkzeug.security import check_password_hash, generate_password_hash

from app.repositories import usuario_repository
from app.utils.auth import (
    cerrar_sesion as util_cerrar_sesion,
    datos_publicos_usuario,
    iniciar_sesion as util_iniciar_sesion,
)


def registrar_nuevo_usuario(nombre, email, password):
    existente = usuario_repository.buscar_por_email(email)
    if existente:
        return None, "EMAIL_DUPLICADO", "El email ya está registrado", 409

    password_hash = generate_password_hash(password)
    id_nuevo = usuario_repository.crear_usuario(nombre, email, password_hash, "CLIENTE")

    usuario = {
        "id_usuario": id_nuevo,
        "nombre": nombre,
        "email": email,
        "rol": "CLIENTE",
    }

    return datos_publicos_usuario(usuario), None, None, 201


def autenticar_usuario(email, password):
    usuario = usuario_repository.buscar_por_email(email)

    if not usuario or not check_password_hash(usuario["password_hash"], password):
        return None, "CREDENCIALES_INVALIDAS", "Credenciales inválidas", 401

    util_iniciar_sesion(usuario)
    return datos_publicos_usuario(usuario), None, None, 200


def cerrar_sesion_activa():
    util_cerrar_sesion()


def obtener_usuario_actual(id_usuario):
    usuario = usuario_repository.buscar_por_id(id_usuario)
    if not usuario:
        util_cerrar_sesion()
        return None, "NO_AUTENTICADO", "La sesión ya no es válida", 401

    return datos_publicos_usuario(usuario), None, None, 200