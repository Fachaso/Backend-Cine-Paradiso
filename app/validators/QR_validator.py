def validar_qr(datos):
    if not isinstance(datos, dict):
        return None, "La solicitud debe ser un JSON válido"

    if "id_funcion" not in datos:
        return None, "El campo id_funcion es obligatorio"

    id_funcion = datos["id_funcion"]

    if isinstance(id_funcion, bool) or not isinstance(id_funcion, int) or id_funcion <= 0:
        return None, "El id_funcion debe ser un entero positivo"

    return id_funcion, None