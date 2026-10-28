# no hemos fijado cual podria ser el maximo de capacidad
# fijo al menos un minimo de 46 butacas pero no es una desicion fija
MAX_CAPACIDAD_SALA = 200
MIN_CAPACIDAD_SALA = 46

def validar_id_sucursal(id_sucursal):
    if isinstance(id_sucursal, bool) or not isinstance(id_sucursal, int) or id_sucursal <= 0:
        return False, "El id de sucursal debe ser un entero positivo"

    return True, None


def validar_datos_sala(datos):
    if not isinstance(datos, dict):
        return None, "El cuerpo de la solicitud debe ser un JSON válido"

    campos_requeridos = ("id_sucursal", "nombre", "capacidad")
    for campo in campos_requeridos:
        if campo not in datos:
            return None, f"El campo {campo} es obligatorio"
    for campo in datos:
        if campo not in campos_requeridos:
            return None, f"El campo {campo} no es válido"
    id_sucursal = datos["id_sucursal"]
    es_valido, mensaje = validar_id_sucursal(id_sucursal)
    if not es_valido:
        return None, mensaje

    nombre = datos["nombre"]
    if not isinstance(nombre, str) or not nombre.strip():
        return None, "El nombre debe ser un texto no vacío"
    nombre = nombre.strip()
    if len(nombre) > 100:
        return None, "El nombre no puede superar los 100 caracteres"

    capacidad = datos["capacidad"]
    if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
        return None, "La capacidad debe ser un entero positivo"
    if capacidad > MAX_CAPACIDAD_SALA:
        return None, "La capacidad supera el máximo permitido por la base de datos"
    if capacidad < MIN_CAPACIDAD_SALA:
        return None, "La capacidad es menor al mínimo permitido para una sala de cine"
    return {
        "id_sucursal": id_sucursal,
        "nombre": nombre,
        "capacidad": capacidad,
    }, None


def obtener_rol_de_sesion(sesion):
    rol = None

    if "id_usuario" in sesion and "rol" in sesion:
        rol = sesion["rol"]

    return rol