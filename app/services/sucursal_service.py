from app.repositories import sucursal_repository


def listar_sucursales_activas():
    return sucursal_repository.listar_sucursales_activas()


def obtener_salas_de_sucursal(id_sucursal):
    sucursal = sucursal_repository.obtener_sucursal_por_id(id_sucursal)
    if not sucursal:
        return None, "SUCURSAL_NO_ENCONTRADA"

    return sucursal_repository.listar_salas_por_sucursal(id_sucursal), None


def generar_etiqueta_fila(indice):
    """Convierte 1, 26 y 27 en A, Z y AA respectivamente."""
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
        asientos.append({"fila": fila, "numero": numero})
    return asientos


def crear_sala(datos_sala):
    if not sucursal_repository.obtener_sucursal_por_id(datos_sala["id_sucursal"]):
        return None, "SUCURSAL_NO_ENCONTRADA"

    if sucursal_repository.sala_existe_en_sucursal(
        datos_sala["id_sucursal"], datos_sala["nombre"]
    ):
        return None, "SALA_DUPLICADA"

    asientos = generar_asientos(datos_sala["capacidad"])
    return sucursal_repository.crear_sala_con_asientos(datos_sala, asientos), None
