from datetime import datetime
from decimal import Decimal

from app.repositories.estadisticas_repository import (
    obtener_cancelaciones_db,
    obtener_franjas_horarias_db,
    obtener_ocupacion_db,
    obtener_ventas_por_genero_db,
)


def obtener_ocupacion_service(id_funcion=None, id_pelicula=None):
    """
    Calcula el porcentaje de ocupación por funcion y da formato ISO a las fechas.
    """
    filas = obtener_ocupacion_db(
        id_funcion=id_funcion,
        id_pelicula=id_pelicula
    )
    resultado = []

    for fila in filas:
        capacidad = int(fila["capacidad"])
        entradas_vendidas = int(fila["entradas_vendidas"])

        porcentaje = (
            entradas_vendidas / capacidad * 100.0
        ) if capacidad > 0 else 0.0

        porcentaje_ocupacion = round(float(porcentaje), 2)

        fecha_hora = fila["fecha_hora"]
        fecha_hora_str = (
            fecha_hora.isoformat()
            if isinstance(fecha_hora, datetime)
            else str(fecha_hora)
        )

        resultado.append({
            "id_funcion": int(fila["id_funcion"]),
            "titulo_pelicula": str(fila["titulo_pelicula"]),
            "nombre_sala": str(fila["nombre_sala"]),
            "fecha_hora": fecha_hora_str,
            "capacidad": capacidad,
            "entradas_vendidas": entradas_vendidas,
            "porcentaje_ocupacion": porcentaje_ocupacion,
        })

    return resultado, None, 200


def obtener_ventas_por_genero_service():
    """
    Convierte los importes a numeros compatibles con JSON
    y estructura las ventas por genero cinematografico.
    """
    filas = obtener_ventas_por_genero_db()
    resultado = []

    for fila in filas:
        monto = fila["total_ventas"]

        total_ventas = (
            float(monto)
            if isinstance(monto, Decimal)
            else float(monto or 0.0)
        )

        resultado.append({
            "genero": str(fila["genero"]),
            "total_ventas": round(total_ventas, 2),
            "entradas_vendidas": int(fila["entradas_vendidas"]),
        })

    return resultado, None, 200


def obtener_franjas_horarias_service():
    """
    Formatea la cantidad de entradas vendidas por horario de funcion.
    """
    filas = obtener_franjas_horarias_db()
    resultado = []

    for fila in filas:
        resultado.append({
            "hora": str(fila["hora"]),
            "entradas_vendidas": int(fila["entradas_vendidas"]),
        })

    return resultado, None, 200


def obtener_cancelaciones_service():
    """
    Obtiene el resumen de compras canceladas segun el estado del codigo QR.
    """
    total = obtener_cancelaciones_db()

    data = {
        "total_cancelaciones": int(total)
    }

    return data, None, 200