from datetime import datetime, timedelta, timezone
import math


def validar_datos_funcion(datos):
    datos_validados = None
    error = None
    campos_requeridos = ("id_pelicula", "id_sala", "fecha_hora", "precio_entrada")

    if not isinstance(datos, dict) or not datos:
        error = "El cuerpo de la solicitud debe ser un JSON válido"
    else:
        for campo in campos_requeridos:
            if campo not in datos and error is None:
                error = f"El campo {campo} es obligatorio"

        for campo in datos:
            if campo not in campos_requeridos and error is None:
                error = f"El campo {campo} no es válido"

        if error is None:
            id_pelicula = datos["id_pelicula"]
            if (isinstance(id_pelicula, bool) or
                    not isinstance(id_pelicula, int) or id_pelicula <= 0):
                error = "El id de película debe ser un entero positivo"

        if error is None:
            id_sala = datos["id_sala"]
            if isinstance(id_sala, bool) or not isinstance(id_sala, int) or id_sala <= 0:
                error = "El id de sala debe ser un entero positivo"

        fecha_argentina = None
        if error is None:
            fecha_hora = datos["fecha_hora"]
            if not isinstance(fecha_hora, str):
                error = "La fecha y hora debe ser un texto válido"
            else:
                try:
                    fecha_con_zona = datetime.fromisoformat(fecha_hora)
                    if fecha_con_zona.tzinfo is None:
                        error = "La fecha y hora debe incluir zona horaria"
                    else:
                        zona_argentina = timezone(timedelta(hours=-3))
                        fecha_argentina = fecha_con_zona.astimezone(zona_argentina)
                        fecha_argentina = fecha_argentina.replace(tzinfo=None)
                except ValueError:
                    error = "La fecha y hora debe tener formato ISO 8601 válido"

        if error is None:
            precio_entrada = datos["precio_entrada"]
            if (isinstance(precio_entrada, bool) or
                    not isinstance(precio_entrada, (int, float)) or
                    (isinstance(precio_entrada, float) and
                     not math.isfinite(precio_entrada)) or precio_entrada < 0):
                error = "El precio de entrada debe ser un número mayor o igual a cero"

        if error is None:
            datos_validados = {
                "id_pelicula": id_pelicula,
                "id_sala": id_sala,
                "fecha_hora": fecha_argentina,
                "precio_entrada": precio_entrada,
            }

    return datos_validados, error
