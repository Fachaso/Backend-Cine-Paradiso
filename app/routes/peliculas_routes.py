from flask import Blueprint
from app.controllers.pelicula_controller import (
    listar_peliculas,
    obtener_pelicula_por_id,
    buscar_peliculas_externas,
    crear_pelicula,
)

pelicula_bp = Blueprint("peliculas", __name__, url_prefix="/api/peliculas")

# Rutas de búsqueda e importación de catálogo (US-04)
pelicula_bp.route("/buscar-externa", methods=["GET"])(buscar_peliculas_externas)
pelicula_bp.route("", methods=["POST"])(crear_pelicula)

# Rutas de consulta del catálogo local
pelicula_bp.route("", methods=["GET"])(listar_peliculas)
pelicula_bp.route("/<int:id_pelicula>", methods=["GET"])(obtener_pelicula_por_id)
