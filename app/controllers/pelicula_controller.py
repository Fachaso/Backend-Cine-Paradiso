from flask import jsonify, request
from app.repositories.db_connection import execute_query
from app.services.tmdb_service import buscar_peliculas_en_tmdb
from app.repositories.pelicula_repository import (
    existe_pelicula_por_titulo,
    insertar_pelicula,
)
from app.validators.pelicula_validator import (
    validar_datos_pelicula,
    validar_parametro_busqueda,
)

def listar_peliculas():
    """
    Controlador para listar películas desde la base de datos MySQL (SQL Puro).
    """
    try:
        pagina = request.args.get('pagina', 1, type=int)
        limite = request.args.get('limite', 10, type=int)
        genero = request.args.get('genero', type=str)
        buscar = request.args.get('buscar', type=str)
        estado = request.args.get('estado', type=str)

        if pagina < 1:
            pagina = 1
        if limite < 1:
            limite = 1
        if limite > 50:
            limite = 50
        offset = (pagina - 1) * limite

        clausulas = []
        parametros = []

        if genero:
            clausulas.append("genero = %s")
            parametros.append(genero)
        if buscar:
            clausulas.append("titulo LIKE %s")
            parametros.append(f"%{buscar}%")
        where_sql = f" WHERE {' AND '.join(clausulas)}" if clausulas else ""

        count_sql = f"SELECT COUNT(*) as total FROM peliculas{where_sql}"
        count_result = execute_query(count_sql, tuple(parametros), fetchone=True)
        total = count_result["total"] if count_result else 0


        sql = f"SELECT id_pelicula, titulo, sinopsis, poster_url, genero, duracion_min, clasificacion FROM peliculas{where_sql} LIMIT %s OFFSET %s"
        query_params = tuple(parametros) + (limite, offset)
        peliculas = execute_query(sql, query_params, fetchall=True) or []
        total_paginas = (total + limite - 1) // limite if total > 0 else 0

        return jsonify({
            "status": "success",
            "data": peliculas,
            "pagination": {
                "pagina": pagina,
                "limite": limite,
                "total": total,
                "total_paginas": total_paginas,
            }

        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": f"Error al obtener películas: {str(error)}"
        }), 500

def obtener_pelicula_por_id(id_pelicula):
    """
    Controlador para obtener el detalle de una película por ID.
    """
    try:
        sql = "SELECT id_pelicula, titulo, sinopsis, poster_url, genero, duracion_min, clasificacion FROM peliculas WHERE id_pelicula = %s"
        pelicula = execute_query(sql, (id_pelicula,), fetchone=True)
        
        if not pelicula:
            return jsonify({
                "status": "error",
                "code": "PELICULA_NO_ENCONTRADA",
                "message": "Película no encontrada"
            }), 404
            
        return jsonify({
            "status": "success",
            "data": pelicula
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": f"Error al consultar película: {str(error)}"
        }), 500

def buscar_peliculas_externas():
    """
    GET /api/peliculas-externas?q=...
    Consulta la API externa de TMDb en español y retorna candidatos para importar.
    """
    texto_busqueda = request.args.get("q")
    es_valido, mensaje_error = validar_parametro_busqueda(texto_busqueda)
    if not es_valido:
        return jsonify({
            "status": "error",
            "code": "PARAMETRO_FALTANTE",
            "message": mensaje_error
        }), 400

    try:
        peliculas = buscar_peliculas_en_tmdb(texto_busqueda.strip())
        return jsonify({
            "status": "success",
            "data": peliculas
        }), 200
    except ValueError as error_valor:
        return jsonify({
            "status": "error",
            "code": "ERROR_CONFIGURACION",
            "message": str(error_valor)
        }), 500
    except PermissionError as error_permiso:
        return jsonify({
            "status": "error",
            "code": "ERROR_AUTORIZACION_EXTERNA",
            "message": str(error_permiso)
        }), 500
    except Exception as error_general:
        return jsonify({
            "status": "error",
            "code": "ERROR_SERVICIO_EXTERNO",
            "message": f"Error al consultar servicio externo: {str(error_general)}"
        }), 500

def crear_pelicula():
    """
    POST /api/peliculas
    Da de alta una película en el catálogo local.
    """
    datos = request.get_json(silent=True)
    datos_pelicula, mensaje_error = validar_datos_pelicula(datos)
    if mensaje_error:
        return jsonify({
            "status": "error",
            "code": "DATOS_INVALIDOS",
            "message": mensaje_error
        }), 400

    try:
        if existe_pelicula_por_titulo(datos_pelicula["titulo"]):
            return jsonify({
                "status": "error",
                "code": "PELICULA_DUPLICADA",
                "message": f"Ya existe una película con el título '{datos_pelicula['titulo']}'"
            }), 409

        id_nuevo = insertar_pelicula(
            titulo=datos_pelicula["titulo"],
            sinopsis=datos_pelicula["sinopsis"],
            poster_url=datos_pelicula["poster_url"],
            genero=datos_pelicula["genero"],
            duracion_min=datos_pelicula["duracion_min"],
            clasificacion=datos_pelicula["clasificacion"]
        )

        pelicula_creada = {
            "id_pelicula": id_nuevo,
            **datos_pelicula
        }

        return jsonify({
            "status": "success",
            "data": pelicula_creada
        }), 201

    except Exception as error_bd:
        return jsonify({
            "status": "error",
            "code": "ERROR_INTERNO",
            "message": f"Error al registrar película en la base de datos: {str(error_bd)}"
        }), 500
