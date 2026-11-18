def validar_solicitud_recuperacion(datos):
    email = str(datos.get("email", "")).strip().lower()
    frontend_url = str(datos.get("frontend_url", "")).strip().rstrip("/")

    if not email or "@" not in email:
        return False, "EMAIL_INVALIDO", "Ingresá un correo electrónico válido", None

    return True, None, None, (email, frontend_url)


def validar_restablecimiento_password(datos):
    token = str(datos.get("token", "")).strip()
    password = str(datos.get("password", ""))

    if not token:
        return False, "TOKEN_INVALIDO", "El enlace de recuperación no es válido", None

    if len(password) < 6:
        return False, "PASSWORD_INVALIDA", "La contraseña debe tener al menos 6 caracteres", None

    return True, None, None, (token, password)