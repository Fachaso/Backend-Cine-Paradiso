from app.repositories import resena_repository
from app.validators.resena_validator import validar_datos_resena


def listar_resenas(id_pelicula):
    if not resena_repository.existe_pelicula(id_pelicula):
        return None, "PELICULA_NO_ENCONTRADA"
    return resena_repository.listar_resenas_por_pelicula(id_pelicula), None


def crear_resena(id_usuario, id_pelicula, datos):
    if not resena_repository.existe_pelicula(id_pelicula):
        return None, "PELICULA_NO_ENCONTRADA", "Película no encontrada"

    datos_limpios, mensaje = validar_datos_resena(datos)
    if mensaje:
        return None, "DATOS_INVALIDOS", mensaje

    if not resena_repository.usuario_asistio_a_pelicula(id_usuario, id_pelicula):
        return None, "RESENA_NO_HABILITADA", "Solo podés reseñar películas que viste en una compra con QR validado"

    if resena_repository.existe_resena_de_usuario(id_usuario, id_pelicula):
        return None, "RESENA_DUPLICADA", "Ya reseñaste esta película"

    id_nueva = resena_repository.crear_resena(
        id_usuario, id_pelicula,
        datos_limpios["puntuacion"], datos_limpios["comentario"],
    )
    return resena_repository.obtener_resena_por_id(id_nueva), None, None