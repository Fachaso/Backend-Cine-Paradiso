from app.services.tmdb_service import buscar_peliculas_en_tmdb
from app.repositories.pelicula_repository import actualizar_poster_pelicula
from app.repositories.db_connection import execute_query


PELICULAS_INICIALES = [
    ("Inception", 2010),
    ("Interstellar", 2014),
    ("The Dark Knight", 2008),
    ("Spider-Man: Across the Spider-Verse", 2023),
    ("Avatar: The Way of Water", 2022),
]


def sincronizar_posteres_iniciales():
    """
    Obtiene desde TMDb los pósteres faltantes o temporales
    de las cinco películas iniciales.
    """

    for titulo, anio in PELICULAS_INICIALES:
        try:
            registro = execute_query(
                """
                SELECT id_pelicula, poster_url
                FROM peliculas
                WHERE titulo = %s
                """,
                (titulo,),
                fetchone=True
            )

            if not registro:
                continue

            poster_actual = registro["poster_url"]

            if poster_actual and "via.placeholder.com" not in poster_actual:
                continue

            resultados = buscar_peliculas_en_tmdb(titulo)

            coincidencia = next(
                (
                    resultado for resultado in resultados
                    if resultado["anio"] == anio
                    and resultado["poster_url"]
                ),
                None
            )

            if coincidencia:
                actualizar_poster_pelicula(
                    registro["id_pelicula"],
                    coincidencia["poster_url"]
                )
                print(f"Póster actualizado: {titulo}")

        except Exception as error:
            print(f"No se pudo sincronizar el póster de {titulo}: {error}")