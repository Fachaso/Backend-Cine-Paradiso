TIPOS_VALIDOS = ("COMIDA", "BEBIDA", "COMBO", "ESTACIONAMIENTO", "VIP", "OTRO")
CAMPOS_PERMITIDOS = ("nombre", "descripcion", "tipo", "precio")


def validar_datos_servicio(datos):
    if not isinstance(datos, dict):
        return None, "El cuerpo de la solicitud debe ser un JSON válido"

    for campo in datos:
        if campo not in CAMPOS_PERMITIDOS:
            return None, f"El campo {campo} no es válido"

    for campo in ("nombre", "tipo", "precio"):
        if campo not in datos:
            return None, f"El campo {campo} es obligatorio"

    nombre = datos["nombre"]
    if not isinstance(nombre, str) or not nombre.strip():
        return None, "El nombre debe ser un texto no vacío"
    nombre = nombre.strip()
    if len(nombre) > 100:
        return None, "El nombre no puede superar los 100 caracteres"

    descripcion = datos.get("descripcion")
    if descripcion is not None:
        if not isinstance(descripcion, str):
            return None, "La descripción debe ser un texto"
        descripcion = descripcion.strip()
        if len(descripcion) > 255:
            return None, "La descripción no puede superar los 255 caracteres"

    tipo = datos["tipo"]
    if tipo not in TIPOS_VALIDOS:
        return None, "El tipo debe ser uno de: " + ", ".join(TIPOS_VALIDOS)

    precio = datos["precio"]
    if isinstance(precio, bool) or not isinstance(precio, (int, float)) or precio < 0:
        return None, "El precio debe ser un número mayor o igual a 0"

    return {
        "nombre": nombre,
        "descripcion": descripcion,
        "tipo": tipo,
        "precio": precio,
    }, None