from flask import jsonify
from app.repositories.db_connection import execute_query

def listar_peliculas():
    """
    Controlador para listar películas desde la base de datos MySQL (SQL Puro).
    """
    try:
        sql = "SELECT id_pelicula, titulo, sinopsis, poster_url, genero, duracion_min, clasificacion, estado FROM peliculas WHERE estado = 'ACTIVO'"
        peliculas = execute_query(sql, fetchall=True)
        return jsonify({
            "status": "success",
            "data": peliculas
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener películas: {str(e)}"
        }), 500

def obtener_pelicula_por_id(id_pelicula):
    """
    Controlador para obtener el detalle de una película por ID.
    """
    try:
        sql = "SELECT id_pelicula, titulo, sinopsis, poster_url, genero, duracion_min, clasificacion, estado FROM peliculas WHERE id_pelicula = %s"
        pelicula = execute_query(sql, (id_pelicula,), fetchone=True)
        
        if not pelicula:
            return jsonify({
                "status": "error",
                "message": "Película no encontrada"
            }), 404
            
        return jsonify({
            "status": "success",
            "data": pelicula
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al consultar película: {str(e)}"
        }), 500
