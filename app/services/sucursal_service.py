from app.repositories import sucursal_repository
from app.repositories.funcion_repository import obtener_sala_por_id


def listar_sucursales():
    return sucursal_repository.listar_sucursales()


def obtener_salas_de_sucursal(id_sucursal):
    sucursal = sucursal_repository.obtener_sucursal_por_id(id_sucursal)

    if not sucursal:
        return None, "SUCURSAL_NO_ENCONTRADA"

    return sucursal_repository.listar_salas_por_sucursal(id_sucursal), None


def generar_etiqueta_fila(indice):
    """Convierte 1, 26 y 27 en A, Z y AA
    con el limite actual de 200 butacas solo seria necesario hasta la fila T
    pero se deja la funcion para que pueda crecer un poco mas sin problemas"""
    etiqueta = ""

    while indice > 0:
        indice, resto = divmod(indice - 1, 26)
        etiqueta = chr(65 + resto) + etiqueta

    return etiqueta


def generar_asientos(capacidad):
    asientos = []

    for indice in range(capacidad):
        fila = generar_etiqueta_fila((indice // 10) + 1)
        numero = str((indice % 10) + 1)

        asientos.append({
            "fila": fila,
            "numero": numero
        })

    return asientos


def crear_sala(id_sucursal, datos_sala):
    if not sucursal_repository.obtener_sucursal_por_id(id_sucursal):
        return None, "SUCURSAL_NO_ENCONTRADA"

    if sucursal_repository.sala_existe_en_sucursal(
        id_sucursal, datos_sala["nombre"]
    ):
        return None, "SALA_DUPLICADA"

    asientos = generar_asientos(datos_sala["capacidad"])

    return sucursal_repository.crear_sala_con_asientos(
        id_sucursal, datos_sala, asientos
    ), None


def eliminar_sala(id_sucursal, id_sala):
    resultado = None
    error = None
    mensaje = None
    codigo_http = 200

    if not sucursal_repository.obtener_sucursal_por_id(id_sucursal):
        error, mensaje, codigo_http = "SUCURSAL_NO_ENCONTRADA", "La sucursal no existe", 404
    else:
        sala = obtener_sala_por_id(id_sala)
        if not sala or sala["id_sucursal"] != id_sucursal:
            error, mensaje, codigo_http = "SALA_NO_ENCONTRADA", "La sala no existe en la sucursal", 404
        elif sucursal_repository.existen_funciones_de_sala(id_sala):
            error, mensaje, codigo_http = "SALA_CON_FUNCIONES", "No se puede eliminar la sala porque tiene funciones asociadas", 409
        elif sucursal_repository.existen_entradas_de_sala(id_sala):
            error, mensaje, codigo_http = "SALA_CON_ENTRADAS", "No se puede eliminar la sala porque tiene entradas asociadas", 409
        elif sucursal_repository.eliminar_sala(id_sucursal, id_sala) == 1:
            resultado = {"id_sucursal": id_sucursal, "id_sala": id_sala}
        else:
            sala = obtener_sala_por_id(id_sala)

            if not sala or sala["id_sucursal"] != id_sucursal:
                error = "SALA_NO_ENCONTRADA"
                mensaje = "La sala no existe en la sucursal"
                codigo_http = 404
            else:
                error = "ERROR_ELIMINAR_SALA"
                mensaje = "No fue posible eliminar la sala"
                codigo_http = 500
    return resultado, error, mensaje, codigo_http
