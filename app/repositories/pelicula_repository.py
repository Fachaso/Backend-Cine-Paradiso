from app.repositories.db_connection import execute_query

def existe_pelicula_por_titulo(titulo):
    """
    Verifica si ya existe una película activa con el mismo título (case-insensitive).
    """
    consulta_sql = "SELECT id_pelicula FROM peliculas WHERE LOWER(TRIM(titulo)) = LOWER(TRIM(%s)) AND estado = 'ACTIVO'"
    resultado = execute_query(consulta_sql, (titulo,), fetchone=True)
    return resultado is not None

def insertar_pelicula(titulo, sinopsis, poster_url, genero, duracion_min, clasificacion):
    """
    Inserta una nueva película en la tabla peliculas mediante SQL explícito sin ORM.
    Retorna el ID de la película recién creada.
    """
    consulta_sql = """
        INSERT INTO peliculas (titulo, sinopsis, poster_url, genero, duracion_min, clasificacion, estado)
        VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVO')
    """
    parametros = (titulo, sinopsis, poster_url, genero, duracion_min, clasificacion)
    id_creado = execute_query(consulta_sql, parametros, commit=True)
    return id_creado

