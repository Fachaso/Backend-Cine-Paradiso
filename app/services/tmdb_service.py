import os
import requests
from concurrent.futures import ThreadPoolExecutor

URL_BASE_TMDB = "https://api.themoviedb.org/3"
URL_IMAGENES_TMDB = "https://image.tmdb.org/t/p/w500"

def extraer_clasificacion(datos_fechas_estreno, es_adulto=False):
    """
    Extrae la clasificación por edades priorizando Argentina (AR) o España (ES) / Estados Unidos (US).
    """
    if es_adulto:
        return "+18"

    mapa_certificaciones = {
        "G": "ATP",
        "PG": "+13",
        "PG-13": "+13",
        "R": "+16",
        "NC-17": "+18",
        "A": "ATP",
        "B": "+13",
        "C": "+16",
        "D": "+18",
        "7": "+7",
        "12": "+13",
        "16": "+16",
        "18": "+18"
    }

    listado_paises = datos_fechas_estreno.get("results", []) if isinstance(datos_fechas_estreno, dict) else []

    # Prioridad 1: Argentina
    for pais in listado_paises:
        if pais.get("iso_3166_1") == "AR":
            for estreno in pais.get("release_dates", []):
                certificacion = str(estreno.get("certification", "")).strip()
                if certificacion:
                    if certificacion.startswith("+") or certificacion == "ATP":
                        return certificacion
                    return mapa_certificaciones.get(certificacion, f"+{certificacion}")

    # Prioridad 2: España o Estados Unidos
    for pais in listado_paises:
        if pais.get("iso_3166_1") in ("ES", "US"):
            for estreno in pais.get("release_dates", []):
                certificacion = str(estreno.get("certification", "")).strip()
                if certificacion:
                    mapeado = mapa_certificaciones.get(certificacion, certificacion)
                    if mapeado.startswith("+") or mapeado == "ATP":
                        return mapeado
                    return f"+{mapeado}"

    return "+13"

def obtener_detalle_pelicula(id_tmdb, clave_api, idioma="es-ES"):
    """
    Obtiene los detalles completos de una película por su ID de TMDb
    incluyendo duración, géneros y clasificación de edad.
    """
    url_detalle = f"{URL_BASE_TMDB}/movie/{id_tmdb}"
    parametros_consulta = {
        "api_key": clave_api,
        "language": idioma,
        "append_to_response": "release_dates"
    }
    try:
        respuesta = requests.get(url_detalle, params=parametros_consulta, timeout=5)
        if respuesta.status_code != 200:
            return None
        return respuesta.json()
    except requests.exceptions.RequestException:
        return None

def buscar_peliculas_en_tmdb(texto_busqueda, idioma="es-ES", max_resultados=8):
    """
    Busca películas en TMDb por título o palabra clave en español.
    Retorna una lista de diccionarios con el formato PeliculaExternaDTO.
    """
    clave_api = os.getenv("TMDB_API_KEY", "").strip()
    if not clave_api:
        raise ValueError("TMDB_API_KEY no está configurada en las variables de entorno (.env)")

    url_busqueda = f"{URL_BASE_TMDB}/search/movie"
    parametros_busqueda = {
        "api_key": clave_api,
        "query": texto_busqueda,
        "language": idioma,
        "include_adult": False
    }

    try:
        respuesta = requests.get(url_busqueda, params=parametros_busqueda, timeout=5)
        if respuesta.status_code == 401:
            raise PermissionError("La clave de API de TMDb no es válida (401 Unauthorized)")
        respuesta.raise_for_status()
        datos_respuesta = respuesta.json()
    except requests.exceptions.RequestException as error_peticion:
        raise RuntimeError(f"Error al conectar con la API de TMDb: {str(error_peticion)}")

    listado_peliculas_brutas = datos_respuesta.get("results", [])[:max_resultados]
    if not listado_peliculas_brutas:
        return []

    # Consultamos detalles en paralelo para obtener duración y clasificación rápido
    detalles = []
    with ThreadPoolExecutor(max_workers=5) as ejecutor:
        tareas = [ejecutor.submit(obtener_detalle_pelicula, pelicula_cruda["id"], clave_api, idioma) for pelicula_cruda in listado_peliculas_brutas]
        for tarea in tareas:
            detalles.append(tarea.result())

    peliculas_externas = []
    for pelicula_cruda, detalle in zip(listado_peliculas_brutas, detalles):
        datos_origen = detalle if detalle else pelicula_cruda

        titulo = datos_origen.get("title") or pelicula_cruda.get("title") or "Sin título"
        fecha_estreno = datos_origen.get("release_date") or pelicula_cruda.get("release_date") or ""
        anio = int(fecha_estreno[:4]) if len(fecha_estreno) >= 4 and fecha_estreno[:4].isdigit() else None
        sinopsis = datos_origen.get("overview") or pelicula_cruda.get("overview") or ""

        generos = datos_origen.get("genres", [])
        genero = generos[0]["name"] if generos else "General"

        duracion_min = datos_origen.get("runtime") or 120
        datos_fechas_estreno = datos_origen.get("release_dates", {})
        es_adulto = datos_origen.get("adult", False)
        clasificacion = extraer_clasificacion(datos_fechas_estreno, es_adulto)

        ruta_poster = datos_origen.get("poster_path") or pelicula_cruda.get("poster_path")
        url_afiche = f"{URL_IMAGENES_TMDB}{ruta_poster}" if ruta_poster else None

        peliculas_externas.append({
            "id_externo": str(pelicula_cruda["id"]),
            "titulo": titulo,
            "anio": anio,
            "sinopsis": sinopsis,
            "duracion_min": duracion_min,
            "genero": genero,
            "clasificacion": clasificacion,
            "poster_url": url_afiche
        })

    return peliculas_externas