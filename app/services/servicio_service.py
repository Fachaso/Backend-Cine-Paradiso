from app.repositories import servicio_repository


def listar_servicios():
    return servicio_repository.listar_servicios()


def obtener_servicio(id_servicio):
    servicio = servicio_repository.obtener_servicio_por_id(id_servicio)

    if servicio is None:
        return None, "SERVICIO_NO_ENCONTRADO"

    return servicio, None