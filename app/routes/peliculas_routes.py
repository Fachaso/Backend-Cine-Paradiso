from flask import Blueprint
from app.controllers.pelicula_controller import (
    listar_peliculas,
    obtener_pelicula_por_id,
    buscar_peliculas_externas,
    crear_pelicula,
)

pelicula_bp = Blueprint("peliculas", __name__, url_prefix="/api")

# Rutas de búsqueda e importación de catálogo externo (US-04)
pelicula_bp.route("/peliculas-externas", methods=["GET"])(buscar_peliculas_externas)
pelicula_bp.route("/peliculas", methods=["POST"])(crear_pelicula)

# Rutas de consulta del catálogo local
pelicula_bp.route("/peliculas", methods=["GET"])(listar_peliculas)
pelicula_bp.route("/peliculas/<int:id_pelicula>", methods=["GET"])(obtener_pelicula_por_id)