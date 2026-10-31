def validar_parametro_busqueda(q):
    """
    Valida el parámetro de búsqueda para la consulta externa en TMDb.
    """
    if not q or not isinstance(q, str) or not q.strip():
        return False, "El parámetro de búsqueda 'q' es obligatorio"
    return True, None


def validar_datos_pelicula(datos):
    """
    Valida y sanitiza los campos requeridos para importar o dar de alta una película.
    Retorna (datos_limpios, None) si es válido, o (None, mensaje_error) si es inválido.
    """
    if not isinstance(datos, dict):
        return None, "Cuerpo de solicitud inválido o no provisto (se requiere JSON)"

    titulo = datos.get("titulo")
    if not isinstance(titulo, str) or not titulo.strip():
        return None, "El campo 'titulo' es obligatorio"
    titulo = titulo.strip()
    if len(titulo) > 150:
        return None, "El título no puede superar los 150 caracteres"

    genero = datos.get("genero")
    if not isinstance(genero, str) or not genero.strip():
        return None, "El campo 'genero' es obligatorio"
    genero = genero.strip()
    if len(genero) > 50:
        return None, "El género no puede superar los 50 caracteres"

    clasificacion = datos.get("clasificacion")
    if not isinstance(clasificacion, str) or not clasificacion.strip():
        return None, "El campo 'clasificacion' es obligatorio"
    clasificacion = clasificacion.strip()
    if len(clasificacion) > 20:
        return None, "La clasificación no puede superar los 20 caracteres"

    duracion_cruda = datos.get("duracion_min") if datos.get("duracion_min") is not None else datos.get("duracion_minutos")
    if duracion_cruda is None:
        return None, "El campo 'duracion_min' es obligatorio"

    if isinstance(duracion_cruda, bool):
        return None, "La duración debe ser un número entero positivo"

    try:
        duracion_min = int(duracion_cruda)
        if duracion_min <= 0:
            return None, "La duración debe ser un número entero positivo"
    except (ValueError, TypeError):
        return None, "La duración debe ser un número entero positivo"

    sinopsis = datos.get("sinopsis")
    if sinopsis is not None and isinstance(sinopsis, str) and sinopsis.strip():
        sinopsis = sinopsis.strip()
    else:
        sinopsis = None

    url_poster = datos.get("poster_url") or datos.get("url_poster")
    if url_poster is not None and isinstance(url_poster, str) and url_poster.strip():
        url_poster = url_poster.strip()
    else:
        url_poster = None

    datos_limpios = {
        "titulo": titulo,
        "sinopsis": sinopsis,
        "poster_url": url_poster,
        "genero": genero,
        "duracion_min": duracion_min,
        "clasificacion": clasificacion,
    }

    return datos_limpios, None
