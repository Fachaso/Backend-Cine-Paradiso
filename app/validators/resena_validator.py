CAMPOS_PERMITIDOS = ("puntuacion", "comentario")
LIMITE_COMENTARIO = 1000


def validar_datos_resena(datos):
    if not isinstance(datos, dict):
        return None, "El cuerpo de la solicitud debe ser un JSON válido"

    for campo in datos:
        if campo not in CAMPOS_PERMITIDOS:
            return None, f"El campo {campo} no es válido"

    if "puntuacion" not in datos:
        return None, "El campo puntuacion es obligatorio"

    puntuacion = datos["puntuacion"]
    if isinstance(puntuacion, bool) or not isinstance(puntuacion, int) or not 1 <= puntuacion <= 5:
        return None, "La puntuación debe ser un número entero entre 1 y 5"

    comentario = datos.get("comentario")
    if comentario is not None:
        if not isinstance(comentario, str):
            return None, "El comentario debe ser un texto"
        comentario = comentario.strip() or None
        if comentario is not None and len(comentario) > LIMITE_COMENTARIO:
            return None, f"El comentario no puede superar los {LIMITE_COMENTARIO} caracteres"

    return {"puntuacion": puntuacion, "comentario": comentario}, None