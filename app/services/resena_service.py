from app.repositories import resena_repository


def listar_resenas(id_pelicula):
    if not resena_repository.existe_pelicula(id_pelicula):
        return None, "PELICULA_NO_ENCONTRADA"
    return resena_repository.listar_resenas_por_pelicula(id_pelicula), None