from flask import jsonify, request
from app.repositories.db_connection import execute_query

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

        if estado:
            clausulas.append("estado = %s")
            parametros.append(estado)
        else:
            clausulas.append("estado = %s")
            parametros.append("ACTIVO")

        if genero:
            clausulas.append("genero = %s")
            parametros.append(genero)
        if buscar:
            clausulas.append("titulo LIKE %s")
            parametros.append(f"%{buscar}%")
        where_sql = " AND ".join(clausulas)

        count_sql = f"SELECT COUNT(*) as total FROM peliculas WHERE {where_sql}"
        count_result = execute_query(count_sql, tuple(parametros), fetchone=True)
        total = count_result["total"] if count_result else 0


        sql = f"SELECT id_pelicula, titulo, sinopsis, poster_url, genero, duracion_min, clasificacion, estado FROM peliculas WHERE {where_sql} LIMIT %s OFFSET %s"
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
