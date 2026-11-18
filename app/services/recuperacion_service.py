import os

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import generate_password_hash

from app.repositories import recuperacion_repository
from app.services import recuperacion_email_service

SALT_RECUPERACION = "recuperar-password-cine-paradiso"
EXPIRACION_TOKEN_SEGUNDOS = 1800  # 30 minutos


def _generar_token_recuperacion(usuario):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    payload = {
        "id_usuario": usuario["id_usuario"],
        "email": usuario["email"],
        "fp": usuario["password_hash"][-12:],
    }
    return serializer.dumps(payload, salt=SALT_RECUPERACION)


def solicitar_recuperacion_password(email, frontend_url=""):
    mensaje_generico = (
        "Si el correo está registrado, te enviamos un enlace para restablecer tu contraseña."
    )
    usuario = recuperacion_repository.buscar_usuario_por_email(email)
    if not usuario:
        return {"message": mensaje_generico}, None, None, 200

    base_frontend = (
        frontend_url
        or os.getenv("FRONTEND_URL")
        or "http://localhost:5001"
    ).rstrip("/")

    token = _generar_token_recuperacion(usuario)
    url_recuperacion = f"{base_frontend}/restablecer-password/{token}"

    current_app.logger.info(
        "Enlace de recuperación generado para %s: %s", email, url_recuperacion
    )
    recuperacion_email_service.enviar_correo_recuperacion(
        usuario["email"], usuario["nombre"], url_recuperacion
    )

    return {"message": mensaje_generico}, None, None, 200


def restablecer_password(token, nueva_password):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    try:
        datos = serializer.loads(
            token,
            salt=SALT_RECUPERACION,
            max_age=EXPIRACION_TOKEN_SEGUNDOS,
        )
    except SignatureExpired:
        return None, "TOKEN_EXPIRADO", "El enlace venció. Solicitá uno nuevo.", 400
    except BadSignature:
        return None, "TOKEN_INVALIDO", "El enlace de recuperación no es válido.", 400

    usuario = recuperacion_repository.buscar_usuario_por_email(datos.get("email", ""))
    if (
        not usuario
        or usuario["id_usuario"] != datos.get("id_usuario")
        or usuario["password_hash"][-12:] != datos.get("fp")
    ):
        return None, "TOKEN_USADO", "Este enlace ya fue utilizado o no es válido.", 400

    nuevo_hash = generate_password_hash(nueva_password)
    recuperacion_repository.actualizar_password(usuario["id_usuario"], nuevo_hash)

    return (
        {"message": "Contraseña actualizada correctamente. Ya podés iniciar sesión."},
        None,
        None,
        200,
    )