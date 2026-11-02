TIPOS_VALIDOS = ("COMIDA", "BEBIDA", "COMBO", "ESTACIONAMIENTO", "VIP", "OTRO")
CAMPOS_PERMITIDOS = ("nombre", "descripcion", "tipo", "precio")


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre.strip():
        return None, "El nombre debe ser un texto no vacío"
    nombre = nombre.strip()
    if len(nombre) > 100:
        return None, "El nombre no puede superar los 100 caracteres"
    return nombre, None


def _validar_descripcion(descripcion):
    if descripcion is None:
        return None, None
    if not isinstance(descripcion, str):
        return None, "La descripción debe ser un texto"
    descripcion = descripcion.strip()
    if len(descripcion) > 255:
        return None, "La descripción no puede superar los 255 caracteres"
    return descripcion, None


def _validar_tipo(tipo):
    if tipo not in TIPOS_VALIDOS:
        return None, "El tipo debe ser uno de: " + ", ".join(TIPOS_VALIDOS)
    return tipo, None


def _validar_precio(precio):
    if isinstance(precio, bool) or not isinstance(precio, (int, float)) or precio < 0:
        return None, "El precio debe ser un número mayor o igual a 0"
    return precio, None


VALIDADORES = {
    "nombre": _validar_nombre,
    "descripcion": _validar_descripcion,
    "tipo": _validar_tipo,
    "precio": _validar_precio,
}


def _revisar_campos(datos):
    if not isinstance(datos, dict):
        return "El cuerpo de la solicitud debe ser un JSON válido"
    for campo in datos:
        if campo not in CAMPOS_PERMITIDOS:
            return f"El campo {campo} no es válido"
    return None


def validar_datos_servicio(datos):
    """Para crear: nombre, tipo y precio son obligatorios."""
    mensaje = _revisar_campos(datos)
    if mensaje:
        return None, mensaje

    for campo in ("nombre", "tipo", "precio"):
        if campo not in datos:
            return None, f"El campo {campo} es obligatorio"

    limpios = {}
    for campo in CAMPOS_PERMITIDOS:
        if campo in datos:
            valor, error = VALIDADORES[campo](datos[campo])
            if error:
                return None, error
            limpios[campo] = valor
        else:
            limpios[campo] = None  # solo puede faltar la descripción
    return limpios, None


def validar_actualizacion_servicio(datos):
    """Para modificar: todos los campos son opcionales, pero debe venir al menos uno."""
    mensaje = _revisar_campos(datos)
    if mensaje:
        return None, mensaje

    if not datos:
        return None, "Debe enviar al menos un campo para modificar"

    limpios = {}
    for campo, valor in datos.items():
        valor_limpio, error = VALIDADORES[campo](valor)
        if error:
            return None, error
        limpios[campo] = valor_limpio
    return limpios, None