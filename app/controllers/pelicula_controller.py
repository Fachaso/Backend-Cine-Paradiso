from flask import jsonify, request
from app.repositories.db_connection import execute_query
from app.services.tmdb_service import buscar_peliculas_en_tmdb
from app.repositories.pelicula_repository import (
    existe_pelicula_por_titulo,
    insertar_pelicula,
)

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

def buscar_peliculas_externas():
    """
    GET /api/peliculas/buscar-externa?query=...
    Consulta la API externa de TMDb en español y retorna candidatos para importar.
    """
    texto_busqueda = request.args.get("query", "").strip()
    if not texto_busqueda:
        return jsonify({
            "status": "error",
            "message": "El parámetro de búsqueda 'query' es obligatorio"
        }), 400

    try:
        peliculas = buscar_peliculas_en_tmdb(texto_busqueda)
        return jsonify({
            "status": "success",
            "data": peliculas
        }), 200
    except ValueError as error_valor:
        return jsonify({
            "status": "error",
            "message": str(error_valor)
        }), 500
    except PermissionError as error_permiso:
        return jsonify({
            "status": "error",
            "message": str(error_permiso)
        }), 500
    except Exception as error_general:
        return jsonify({
            "status": "error",
            "message": f"Error al consultar servicio externo: {str(error_general)}"
        }), 500

def crear_pelicula():
    """
    POST /api/peliculas
    Da de alta o importa una película al catálogo local con persistencia en MySQL.
    """
    datos = request.get_json(silent=True)
    if not datos or not isinstance(datos, dict):
        return jsonify({
            "status": "error",
            "message": "Cuerpo de solicitud inválido o no provisto (se requiere JSON)"
        }), 400

    titulo = str(datos.get("titulo", "")).strip()
    genero = str(datos.get("genero", "")).strip()
    clasificacion = str(datos.get("clasificacion", "")).strip()
    sinopsis = str(datos.get("sinopsis", "")).strip()
    url_poster = str(datos.get("poster_url") or datos.get("url_poster") or "").strip()

    duracion_cruda = datos.get("duracion_min") if datos.get("duracion_min") is not None else datos.get("duracion_minutos")

    # Validación de campos obligatorios
    if not titulo:
        return jsonify({"status": "error", "message": "El campo 'titulo' es obligatorio"}), 400
    if not genero:
        return jsonify({"status": "error", "message": "El campo 'genero' es obligatorio"}), 400
    if not clasificacion:
        return jsonify({"status": "error", "message": "El campo 'clasificacion' es obligatorio"}), 400
    if duracion_cruda is None:
        return jsonify({"status": "error", "message": "El campo 'duracion_min' es obligatorio"}), 400

    try:
        duracion_min = int(duracion_cruda)
        if duracion_min <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "La duración debe ser un número entero positivo"}), 400

    # Validación de duplicados
    try:
        if existe_pelicula_por_titulo(titulo):
            return jsonify({
                "status": "error",
                "message": f"Ya existe una película activa con el título '{titulo}'"
            }), 409

        id_nuevo = insertar_pelicula(
            titulo=titulo,
            sinopsis=sinopsis,
            poster_url=url_poster if url_poster else None,
            genero=genero,
            duracion_min=duracion_min,
            clasificacion=clasificacion
        )

        pelicula_creada = {
            "id_pelicula": id_nuevo,
            "titulo": titulo,
            "sinopsis": sinopsis,
            "duracion_min": duracion_min,
            "duracion_minutos": duracion_min,
            "genero": genero,
            "clasificacion": clasificacion,
            "poster_url": url_poster,
            "url_poster": url_poster,
        }

        return jsonify({
            "status": "success",
            "data": pelicula_creada
        }), 201

    except Exception as error_bd:
        return jsonify({
            "status": "error",
            "message": f"Error al registrar película en la base de datos: {str(error_bd)}"
        }), 500
