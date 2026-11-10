def validar_datos_registro(datos):
    nombre = str(datos.get("nombre", "")).strip()
    email = str(datos.get("email", "")).strip().lower()
    password = str(datos.get("password", ""))

    if not nombre or not email or not password:
        return False, "DATOS_INVALIDOS", "Nombre, email y contraseña son obligatorios", None

    if "@" not in email:
        return False, "EMAIL_INVALIDO", "El formato del email es inválido", None

    if len(password) < 6:
        return False, "PASSWORD_INVALIDA", "La contraseña debe tener al menos 6 caracteres", None

    return True, None, None, (nombre, email, password)


def validar_datos_login(datos):
    email = str(datos.get("email", "")).strip().lower()
    password = str(datos.get("password", ""))

    if not email or not password:
        return False, "DATOS_INVALIDOS", "Email y contraseña son obligatorios", None

    return True, None, None, (email, password)