from app.repositories import servicio_repository


def listar_servicios():
    return servicio_repository.listar_servicios()