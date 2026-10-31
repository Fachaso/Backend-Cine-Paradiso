from unittest.mock import MagicMock

import pytest
from flask import Flask
from mysql.connector import Error

from app.repositories import sucursal_repository
from app.routes.sucursales_routes import sucursales_bp
from app.services import sucursal_service


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def crear_cliente():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "pruebas-us07"
    app.config["TESTING"] = True

    app.register_blueprint(sucursales_bp)

    return app.test_client()


def sesion_admin(cliente):
    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1
        sesion["rol"] = "ADMIN"
        sesion["nombre"] = "Administrador"


def sesion_empleado(cliente):
    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 2
        sesion["rol"] = "EMPLEADO"
        sesion["nombre"] = "Empleado"


def crear_conexion_falsa():
    conexion = MagicMock()

    conexion.is_connected.return_value = True
    conexion.cursor.return_value.lastrowid = 11
    conexion.cursor.return_value.fetchall.return_value = []

    return conexion


def crear_sala_simulada(id_sucursal, datos):
    sala = {
        "id_sala": 7,
        "id_sucursal": id_sucursal,
        "nombre": datos["nombre"],
        "capacidad": datos["capacidad"],
        "asientos_creados": datos["capacidad"]
    }

    return sala, None


# ============================================================
# PRUEBAS DE LISTADO DE SUCURSALES
# ============================================================

def test_lista_sucursales_ordenadas_con_ciudad(monkeypatch):
    esperado = [
        {
            "id_sucursal": 2,
            "nombre": "Centro",
            "direccion": "Direccion B",
            "ciudad": "Buenos Aires"
        },
        {
            "id_sucursal": 1,
            "nombre": "Norte",
            "direccion": "Direccion A",
            "ciudad": "Tigre"
        }
    ]

    monkeypatch.setattr(
        sucursal_service,
        "listar_sucursales",
        lambda: esperado
    )

    cliente = crear_cliente()
    respuesta = cliente.get("/api/sucursales")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        "status": "success",
        "data": esperado
    }


def test_lista_sucursales_vacia(monkeypatch):
    monkeypatch.setattr(
        sucursal_service,
        "listar_sucursales",
        lambda: []
    )

    cliente = crear_cliente()
    respuesta = cliente.get("/api/sucursales")

    assert respuesta.status_code == 200
    assert respuesta.get_json()["data"] == []


# ============================================================
# PRUEBAS DE AUTENTICACION Y AUTORIZACION
# ============================================================

def test_listar_salas_sin_autenticacion(monkeypatch):
    cliente = crear_cliente()

    monkeypatch.setattr(
        sucursal_service,
        "obtener_salas_de_sucursal",
        lambda id_sucursal: ([], None)
    )

    respuesta = cliente.get("/api/sucursales/1/salas")

    assert respuesta.status_code == 200
    assert respuesta.get_json()["status"] == "success"


def test_listar_salas_como_empleado(monkeypatch):
    cliente = crear_cliente()
    sesion_empleado(cliente)

    monkeypatch.setattr(
        sucursal_service,
        "obtener_salas_de_sucursal",
        lambda id_sucursal: ([], None)
    )

    respuesta = cliente.get("/api/sucursales/1/salas")

    assert respuesta.status_code == 200


def test_listar_salas_como_administrador(monkeypatch):
    cliente = crear_cliente()
    sesion_admin(cliente)

    monkeypatch.setattr(
        sucursal_service,
        "obtener_salas_de_sucursal",
        lambda id_sucursal: ([], None)
    )

    respuesta = cliente.get("/api/sucursales/1/salas")

    assert respuesta.status_code == 200


def test_crear_sala_requiere_admin():
    cliente = crear_cliente()

    datos = {
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json=datos
    )

    assert respuesta.status_code == 401
    assert respuesta.get_json()["code"] == "NO_AUTENTICADO"

    sesion_empleado(cliente)

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json=datos
    )

    assert respuesta.status_code == 403
    assert respuesta.get_json()["code"] == "PERMISOS_INSUFICIENTES"


def test_crear_sala_rechaza_sesion_incompleta():
    cliente = crear_cliente()

    with cliente.session_transaction() as sesion:
        sesion["rol"] = "ADMIN"

    datos = {
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json=datos
    )

    assert respuesta.status_code == 401
    assert respuesta.get_json()["code"] == "NO_AUTENTICADO"


# ============================================================
# PRUEBAS DE LISTADO DE SALAS
# ============================================================

def test_lista_salas_exitosa(monkeypatch):
    cliente = crear_cliente()

    salas = [
        {
            "id_sala": 4,
            "id_sucursal": 1,
            "nombre": "Sala 1",
            "capacidad": 48
        }
    ]

    monkeypatch.setattr(
        sucursal_service,
        "obtener_salas_de_sucursal",
        lambda identificador: (salas, None)
    )

    respuesta = cliente.get("/api/sucursales/1/salas")

    assert respuesta.status_code == 200
    assert respuesta.get_json()["data"] == salas


def test_lista_salas_sucursal_inexistente(monkeypatch):
    cliente = crear_cliente()

    monkeypatch.setattr(
        sucursal_service,
        "obtener_salas_de_sucursal",
        lambda identificador: (
            None,
            "SUCURSAL_NO_ENCONTRADA"
        )
    )

    respuesta = cliente.get("/api/sucursales/99/salas")

    assert respuesta.status_code == 404
    assert respuesta.get_json()["code"] == "SUCURSAL_NO_ENCONTRADA"


def test_lista_salas_id_invalido():
    cliente = crear_cliente()

    respuesta = cliente.get("/api/sucursales/0/salas")

    assert respuesta.status_code == 400
    assert respuesta.get_json()["code"] == "ID_INVALIDO"


# ============================================================
# PRUEBAS DE CREACION DE SALAS
# ============================================================

def test_crear_sala_exitosa(monkeypatch):
    cliente = crear_cliente()
    sesion_admin(cliente)

    monkeypatch.setattr(
        sucursal_service,
        "crear_sala",
        crear_sala_simulada
    )

    datos = {
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json=datos
    )

    assert respuesta.status_code == 201
    assert respuesta.get_json()["status"] == "success"
    assert respuesta.get_json()["data"]["id_sucursal"] == 1
    assert respuesta.get_json()["data"]["capacidad"] == 48
    assert respuesta.get_json()["data"]["asientos_creados"] == 48


def test_crear_sala_valida_limites_de_capacidad(monkeypatch):
    cliente = crear_cliente()
    sesion_admin(cliente)

    monkeypatch.setattr(
        sucursal_service,
        "crear_sala",
        crear_sala_simulada
    )

    for capacidad in (0, -1, 201):
        respuesta = cliente.post(
            "/api/sucursales/1/salas",
            json={
                "nombre": "Sala 4",
                "capacidad": capacidad
            }
        )

        assert respuesta.status_code == 400

    for capacidad in (1, 45, 200):
        respuesta = cliente.post(
            "/api/sucursales/1/salas",
            json={
                "nombre": "Sala 4",
                "capacidad": capacidad
            }
        )

        assert respuesta.status_code == 201


def test_crear_sala_rechaza_campos_desconocidos():
    cliente = crear_cliente()
    sesion_admin(cliente)

    datos = {
        "nombre": "Sala 4",
        "capacidad": 48,
        "precio": 5000
    }

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json=datos
    )

    assert respuesta.status_code == 400
    assert respuesta.get_json()["code"] == "DATOS_INVALIDOS"


def test_crear_sala_rechaza_id_sucursal_en_json():
    cliente = crear_cliente()
    sesion_admin(cliente)

    datos = {
        "id_sucursal": 1,
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json=datos
    )

    assert respuesta.status_code == 400
    assert respuesta.get_json()["code"] == "DATOS_INVALIDOS"


@pytest.mark.parametrize(
    "datos",
    [
        {
            "nombre": "Sala 4"
        },
        {
            "nombre": "",
            "capacidad": 48
        },
        {
            "nombre": "Sala 4",
            "capacidad": "48"
        },
        {
            "nombre": "Sala 4",
            "capacidad": True
        },
        {
            "capacidad": 48
        },
        {
            "nombre": None,
            "capacidad": 48
        },
        {
            "nombre": "Sala 4",
            "capacidad": None
        }
    ]
)
def test_crear_sala_rechaza_datos_invalidos(datos):
    cliente = crear_cliente()
    sesion_admin(cliente)

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json=datos
    )

    assert respuesta.status_code == 400
    assert respuesta.get_json()["code"] == "DATOS_INVALIDOS"


def test_crear_sala_rechaza_nombre_mayor_a_150_caracteres(monkeypatch):
    cliente = crear_cliente()
    sesion_admin(cliente)

    def servicio_no_debe_ejecutarse(*args, **kwargs):
        pytest.fail(
            "No debe llamarse al servicio si el nombre supera 150 caracteres"
        )

    monkeypatch.setattr(
        sucursal_service,
        "crear_sala",
        servicio_no_debe_ejecutarse
    )

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json={
            "nombre": "A" * 151,
            "capacidad": 48
        }
    )

    assert respuesta.status_code == 400


def test_crear_sala_rechaza_json_invalido():
    cliente = crear_cliente()
    sesion_admin(cliente)

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json=["Sala 4", 48]
    )

    assert respuesta.status_code == 400
    assert respuesta.get_json()["code"] == "DATOS_INVALIDOS"


def test_crear_sala_rechaza_id_sucursal_invalido():
    cliente = crear_cliente()
    sesion_admin(cliente)

    datos = {
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post(
        "/api/sucursales/0/salas",
        json=datos
    )

    assert respuesta.status_code == 400
    assert respuesta.get_json()["code"] == "ID_INVALIDO"


def test_crear_sala_sucursal_inexistente(monkeypatch):
    cliente = crear_cliente()
    sesion_admin(cliente)

    monkeypatch.setattr(
        sucursal_service,
        "crear_sala",
        lambda id_sucursal, datos: (
            None,
            "SUCURSAL_NO_ENCONTRADA"
        )
    )

    datos = {
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post(
        "/api/sucursales/99/salas",
        json=datos
    )

    assert respuesta.status_code == 404
    assert respuesta.get_json()["code"] == "SUCURSAL_NO_ENCONTRADA"


def test_crear_sala_duplicada(monkeypatch):
    cliente = crear_cliente()
    sesion_admin(cliente)

    monkeypatch.setattr(
        sucursal_service,
        "crear_sala",
        lambda id_sucursal, datos: (
            None,
            "SALA_DUPLICADA"
        )
    )

    datos = {
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post(
        "/api/sucursales/1/salas",
        json=datos
    )

    assert respuesta.status_code == 409
    assert respuesta.get_json()["code"] == "SALA_DUPLICADA"


# ============================================================
# PRUEBAS DE GENERACION DE ASIENTOS
# ============================================================

def test_generacion_de_asientos_respeta_capacidad_y_filas():
    asientos = sucursal_service.generar_asientos(46)

    assert len(asientos) == 46

    assert asientos[0] == {
        "fila": "A",
        "numero": "1"
    }

    assert asientos[9] == {
        "fila": "A",
        "numero": "10"
    }

    assert asientos[10] == {
        "fila": "B",
        "numero": "1"
    }

    assert asientos[-1] == {
        "fila": "E",
        "numero": "6"
    }

    asientos_maximos = sucursal_service.generar_asientos(200)

    assert len(asientos_maximos) == 200

    assert asientos_maximos[-1] == {
        "fila": "T",
        "numero": "10"
    }


def test_generacion_de_asientos_no_repite_posiciones():
    asientos = sucursal_service.generar_asientos(200)

    posiciones = [
        (asiento["fila"], asiento["numero"])
        for asiento in asientos
    ]

    assert len(posiciones) == len(set(posiciones))


def test_generacion_de_etiquetas_despues_de_z():
    assert sucursal_service.generar_etiqueta_fila(1) == "A"
    assert sucursal_service.generar_etiqueta_fila(26) == "Z"
    assert sucursal_service.generar_etiqueta_fila(27) == "AA"
    assert sucursal_service.generar_etiqueta_fila(28) == "AB"


# ============================================================
# PRUEBAS DE CREACION EN EL REPOSITORY
# ============================================================

def test_repositorio_crea_sala_y_asientos_con_autocommit(monkeypatch):
    conexion = crear_conexion_falsa()

    monkeypatch.setattr(
        sucursal_repository,
        "get_db_connection",
        lambda: conexion
    )

    id_sucursal = 1

    datos = {
        "nombre": "Sala 4",
        "capacidad": 46
    }

    asientos = sucursal_service.generar_asientos(46)

    resultado = sucursal_repository.crear_sala_con_asientos(
        id_sucursal,
        datos,
        asientos
    )

    cursor = conexion.cursor.return_value

    assert conexion.autocommit is True

    # Una insercion para la sala y 46 para los asientos.
    assert cursor.execute.call_count == 47

    primera_consulta = cursor.execute.call_args_list[0]

    assert "INSERT INTO salas" in primera_consulta.args[0]
    assert primera_consulta.args[1] == (
        1,
        "Sala 4",
        46
    )

    segunda_consulta = cursor.execute.call_args_list[1]

    assert "INSERT INTO asientos" in segunda_consulta.args[0]
    assert segunda_consulta.args[1] == (
        11,
        "A",
        "1"
    )

    assert resultado == {
        "id_sala": 11,
        "id_sucursal": 1,
        "nombre": "Sala 4",
        "capacidad": 46,
        "asientos_creados": 46
    }

    conexion.start_transaction.assert_not_called()
    conexion.commit.assert_not_called()
    conexion.rollback.assert_not_called()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


def test_repositorio_cierra_conexion_si_falla_un_asiento(monkeypatch):
    conexion = crear_conexion_falsa()
    cursor = conexion.cursor.return_value

    def ejecutar_consulta(consulta, parametros=None):
        if "INSERT INTO asientos" in consulta:
            raise Error(msg="Fallo al insertar asiento")

    cursor.execute.side_effect = ejecutar_consulta

    monkeypatch.setattr(
        sucursal_repository,
        "get_db_connection",
        lambda: conexion
    )

    datos = {
        "nombre": "Sala 4",
        "capacidad": 46
    }

    asientos = sucursal_service.generar_asientos(46)

    with pytest.raises(Error):
        sucursal_repository.crear_sala_con_asientos(
            1,
            datos,
            asientos
        )

    assert conexion.autocommit is True

    conexion.start_transaction.assert_not_called()
    conexion.commit.assert_not_called()
    conexion.rollback.assert_not_called()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# PRUEBAS DE CONSULTAS DEL REPOSITORY
# ============================================================

def test_repositorio_lista_sucursales_con_ciudad_y_ordena(monkeypatch):
    conexion = crear_conexion_falsa()

    filas = [
        {
            "id_sucursal": 2,
            "nombre": "Centro",
            "direccion": "Direccion B",
            "ciudad": "Buenos Aires"
        }
    ]

    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = filas

    monkeypatch.setattr(
        sucursal_repository,
        "get_db_connection",
        lambda: conexion
    )

    resultado = sucursal_repository.listar_sucursales()

    consulta = cursor.execute.call_args[0][0]

    assert resultado == filas

    assert "id_sucursal" in consulta
    assert "nombre" in consulta
    assert "direccion" in consulta
    assert "ciudad" in consulta

    assert "WHERE estado" not in consulta
    assert "ORDER BY nombre ASC" in consulta

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


def test_repositorio_lista_salas_sin_estado(monkeypatch):
    conexion = crear_conexion_falsa()

    filas = [
        {
            "id_sala": 4,
            "id_sucursal": 1,
            "nombre": "Sala 1",
            "capacidad": 48
        }
    ]

    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = filas

    monkeypatch.setattr(
        sucursal_repository,
        "get_db_connection",
        lambda: conexion
    )

    resultado = sucursal_repository.listar_salas_por_sucursal(1)

    consulta = cursor.execute.call_args[0][0]

    assert resultado == filas
    assert "id_sala" in consulta
    assert "id_sucursal" in consulta
    assert "nombre" in consulta
    assert "capacidad" in consulta
    assert "estado" not in consulta

    assert cursor.execute.call_args[0][1] == (1,)

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


def test_repositorio_verifica_sucursal_existente(monkeypatch):
    conexion = crear_conexion_falsa()

    sucursal = {
        "id_sucursal": 1
    }

    cursor = conexion.cursor.return_value
    cursor.fetchone.return_value = sucursal

    monkeypatch.setattr(
        sucursal_repository,
        "get_db_connection",
        lambda: conexion
    )

    resultado = sucursal_repository.obtener_sucursal_por_id(1)

    assert resultado == sucursal

    consulta = cursor.execute.call_args[0][0]

    assert "FROM sucursales" in consulta
    assert "WHERE id_sucursal = %s" in consulta

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


def test_repositorio_detecta_sala_duplicada(monkeypatch):
    conexion = crear_conexion_falsa()

    cursor = conexion.cursor.return_value
    cursor.fetchone.return_value = {
        "id_sala": 7
    }

    monkeypatch.setattr(
        sucursal_repository,
        "get_db_connection",
        lambda: conexion
    )

    resultado = sucursal_repository.sala_existe_en_sucursal(
        1,
        "Sala 4"
    )

    assert resultado == {
        "id_sala": 7
    }

    consulta = cursor.execute.call_args[0][0]
    parametros = cursor.execute.call_args[0][1]

    assert "FROM salas" in consulta
    assert "id_sucursal = %s" in consulta
    assert "nombre = %s" in consulta

    assert parametros == (1, "Sala 4")

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()