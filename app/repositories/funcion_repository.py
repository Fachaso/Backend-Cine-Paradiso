from app.repositories.db_connection import get_db_connection


def listar_funciones(id_pelicula=None, id_sucursal=None, fecha=None):
    funciones = None
    conexion = None
    cursor = None
    condiciones = []
    parametros = []

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        if id_pelicula is not None:
            condiciones.append("f.id_pelicula = %s")
            parametros.append(id_pelicula)
        if id_sucursal is not None:
            condiciones.append("s.id_sucursal = %s")
            parametros.append(id_sucursal)
        if fecha is not None:
            condiciones.append("DATE(f.fecha_hora) = %s")
            parametros.append(fecha)

        consulta = (
            "SELECT f.id_funcion, f.id_pelicula, p.titulo AS titulo_pelicula, "
            "p.duracion_min, f.id_sala, s.nombre AS nombre_sala, "
            "s.id_sucursal, su.nombre AS nombre_sucursal, f.fecha_hora, "
            "f.precio_entrada "
            "FROM funciones f "
            "INNER JOIN peliculas p ON f.id_pelicula = p.id_pelicula "
            "INNER JOIN salas s ON f.id_sala = s.id_sala "
            "INNER JOIN sucursales su ON s.id_sucursal = su.id_sucursal"
        )
        if condiciones:
            consulta += " WHERE " + " AND ".join(condiciones)
        consulta += " ORDER BY f.fecha_hora ASC"

        cursor.execute(consulta, tuple(parametros))
        funciones = cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return funciones


def obtener_funcion_por_id(id_funcion):
    funcion = None
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT f.id_funcion, f.id_pelicula, p.titulo AS titulo_pelicula, "
            "p.duracion_min, f.id_sala, s.nombre AS nombre_sala, "
            "s.id_sucursal, su.nombre AS nombre_sucursal, f.fecha_hora, "
            "f.precio_entrada "
            "FROM funciones f "
            "INNER JOIN peliculas p ON f.id_pelicula = p.id_pelicula "
            "INNER JOIN salas s ON f.id_sala = s.id_sala "
            "INNER JOIN sucursales su ON s.id_sucursal = su.id_sucursal "
            "WHERE f.id_funcion = %s",
            (id_funcion,)
        )
        funcion = cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return funcion


def obtener_pelicula_por_id(id_pelicula):
    pelicula = None
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_pelicula, duracion_min "
            "FROM peliculas "
            "WHERE id_pelicula = %s",
            (id_pelicula,)
        )
        pelicula = cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return pelicula


def obtener_sala_por_id(id_sala):
    sala = None
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_sala, id_sucursal "
            "FROM salas "
            "WHERE id_sala = %s",
            (id_sala,)
        )
        sala = cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return sala


def obtener_funciones_de_sala(id_sala):
    funciones = None
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT f.id_funcion, f.fecha_hora, p.duracion_min "
            "FROM funciones f "
            "INNER JOIN peliculas p ON f.id_pelicula = p.id_pelicula "
            "WHERE f.id_sala = %s",
            (id_sala,)
        )
        funciones = cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return funciones


def crear_funcion(datos):
    funcion_creada = None
    conexion = None
    cursor = None

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO funciones (id_pelicula, id_sala, fecha_hora, precio_entrada) "
            "VALUES (%s, %s, %s, %s)",
            (
                datos["id_pelicula"],
                datos["id_sala"],
                datos["fecha_hora"],
                datos["precio_entrada"],
            )
        )
        conexion.commit()
        
        funcion_creada = {
            "id_funcion": cursor.lastrowid,
            "id_pelicula": datos["id_pelicula"],
            "id_sala": datos["id_sala"],
            "fecha_hora": datos["fecha_hora"],
            "precio_entrada": datos["precio_entrada"],
        }
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    return funcion_creada
