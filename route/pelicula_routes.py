from flask import Blueprint
from controllers.pelicula_controller import listar_peliculas, obtener_pelicula_por_id

pelicula_bp = Blueprint("peliculas", __name__, url_prefix="/api/peliculas")

# Definición de rutas utilizando el verbo HTTP correspondiente
pelicula_bp.route("", methods=["GET"])(listar_peliculas)
pelicula_bp.route("/<int:id_pelicula>", methods=["GET"])(obtener_pelicula_por_id)
