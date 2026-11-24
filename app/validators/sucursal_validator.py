MAX_CAPACIDAD_SALA = 200

def validar_id_sucursal(id_sucursal):
    if isinstance(id_sucursal, bool) or not isinstance(id_sucursal, int) or id_sucursal <= 0:
        return False, "El id de sucursal debe ser un entero positivo"

    return True, None

def validar_id_sala(id_sala):
    es_valido = (
        not isinstance(id_sala, bool)
        and isinstance(id_sala, int)
        and id_sala > 0
    )

    mensaje = None

    if not es_valido:
        mensaje = "El id de sala debe ser un entero positivo"

    return es_valido, mensaje

def validar_datos_sala(datos):
    if not isinstance(datos, dict):
        return None, "El cuerpo de la solicitud debe ser un JSON válido"

    campos_requeridos = ("nombre", "filas")
    for campo in campos_requeridos:
        if campo not in datos:
            return None, f"El campo {campo} es obligatorio"
    for campo in datos:
        if campo not in campos_requeridos:
            return None, f"El campo {campo} no es válido"

    nombre = datos["nombre"]
    if not isinstance(nombre, str) or not nombre.strip():
        return None, "El nombre debe ser un texto no vacío"
    nombre = nombre.strip()
    if len(nombre) > 50:
        return None, "El nombre no puede superar los 50 caracteres"

    filas = datos["filas"]
    if not isinstance(filas, list) or not filas:
        return None, "Debe indicar al menos una fila"

    capacidad = 0
    for indice, fila in enumerate(filas, start=1):
        if not isinstance(fila, dict) or set(fila) != {"bloques"}:
            return None, f"La fila {indice} debe contener únicamente el campo bloques"

        bloques = fila["bloques"]
        if not isinstance(bloques, list) or len(bloques) != 3:
            return None, f"La fila {indice} debe tener tres bloques: izquierdo, central y derecho"
        if any(type(cantidad) is not int or cantidad < 0 for cantidad in bloques):
            return None, f"Los bloques de la fila {indice} deben ser enteros no negativos"

        izquierdo, central, derecho = bloques
        if izquierdo > 5 or derecho > 5:
            return None, f"Los bloques laterales de la fila {indice} no pueden superar 5 butacas"
        if central < 1:
            return None, f"El bloque central de la fila {indice} debe tener al menos una butaca"
        if sum(bloques) < 5:
            return None, f"La fila {indice} debe tener al menos 5 butacas"

        capacidad += sum(bloques)
        if capacidad > MAX_CAPACIDAD_SALA:
            return None, "La sala no puede superar las 200 butacas"

    return {
        "nombre": nombre,
        "filas": filas,
    }, None


def obtener_rol_de_sesion(sesion):
    rol = None

    if "id_usuario" in sesion and "rol" in sesion:
        rol = sesion["rol"]

    return rol
