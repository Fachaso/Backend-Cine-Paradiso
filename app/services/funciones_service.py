from datetime import timedelta

from app.repositories.funcion_repository import (
    crear_funcion as crear_funcion_repositorio,
    listar_funciones as listar_funciones_repositorio,
    obtener_funcion_por_id as obtener_funcion_por_id_repositorio,
    obtener_funciones_de_sala,
    obtener_pelicula_por_id,
    obtener_sala_por_id,
)


def listar_funciones(id_pelicula=None, id_sucursal=None, fecha=None):
    funciones = listar_funciones_repositorio(id_pelicula, id_sucursal, fecha)

    return funciones, None, 200


def obtener_funcion_por_id(id_funcion):
    funcion = obtener_funcion_por_id_repositorio(id_funcion)
    error = None
    codigo_http = 200

    if funcion is None:
        error = "La función no existe"
        codigo_http = 404

    return funcion, error, codigo_http


def crear_funcion(datos):
    funcion_creada = None
    error = None
    codigo_http = 201
    pelicula = obtener_pelicula_por_id(datos["id_pelicula"])

    if pelicula is None:
        error = "La película no existe"
        codigo_http = 404
    else:
        duracion_nueva = pelicula["duracion_min"]
        sala = obtener_sala_por_id(datos["id_sala"])

        if sala is None:
            error = "La sala no existe"
            codigo_http = 404
        else:
            funciones_existentes = obtener_funciones_de_sala(datos["id_sala"])
            inicio_nueva = datos["fecha_hora"]
            fin_nueva = inicio_nueva + timedelta(minutes=duracion_nueva)
            hay_superposicion = False

            for funcion_existente in funciones_existentes:
                inicio_existente = funcion_existente["fecha_hora"]
                duracion_existente = funcion_existente["duracion_min"]
                fin_existente = inicio_existente + timedelta(minutes=duracion_existente)

                if inicio_nueva < fin_existente and fin_nueva > inicio_existente:
                    hay_superposicion = True
                    break

            if hay_superposicion:
                error = "La sala ya tiene una función programada en ese horario"
                codigo_http = 409
            else:
                funcion_creada = crear_funcion_repositorio(datos)

    return funcion_creada, error, codigo_http
