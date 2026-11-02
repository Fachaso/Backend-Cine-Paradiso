from app.repositories import servicio_repository
from app.validators.servicio_validator import validar_actualizacion_servicio, validar_datos_servicio


def listar_servicios():
    return servicio_repository.listar_servicios()


def obtener_servicio(id_servicio):
    servicio = servicio_repository.obtener_servicio_por_id(id_servicio)

    if servicio is None:
        return None, "SERVICIO_NO_ENCONTRADO"

    return servicio, None


def crear_servicio(datos):
    datos_limpios, mensaje = validar_datos_servicio(datos)
    if mensaje:
        return None, "DATOS_INVALIDOS", mensaje

    if servicio_repository.existe_servicio_con_nombre(datos_limpios["nombre"]):
        return None, "SERVICIO_DUPLICADO", "Ya existe un servicio con ese nombre"

    id_nuevo = servicio_repository.crear_servicio(
        datos_limpios["nombre"],
        datos_limpios["descripcion"],
        datos_limpios["tipo"],
        datos_limpios["precio"],
    )
    return servicio_repository.obtener_servicio_por_id(id_nuevo), None, None


def actualizar_servicio(id_servicio, datos):
    if servicio_repository.obtener_servicio_por_id(id_servicio) is None:
        return None, "SERVICIO_NO_ENCONTRADO", "El servicio no existe"

    campos, mensaje = validar_actualizacion_servicio(datos)
    if mensaje:
        return None, "DATOS_INVALIDOS", mensaje

    if "nombre" in campos and servicio_repository.existe_otro_servicio_con_nombre(
        campos["nombre"], id_servicio
    ):
        return None, "SERVICIO_DUPLICADO", "Ya existe un servicio con ese nombre"

    servicio_repository.actualizar_servicio(id_servicio, campos)
    return servicio_repository.obtener_servicio_por_id(id_servicio), None, None