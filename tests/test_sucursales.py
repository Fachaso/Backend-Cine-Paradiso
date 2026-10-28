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


def crear_conexion_falsa():
    conexion = MagicMock()

    conexion.is_connected.return_value = True
    conexion.cursor.return_value.lastrowid = 11
    conexion.cursor.return_value.fetchall.return_value = []

    return conexion


def crear_sala_simulada(datos):
    sala = {
        "id_sala": 7,
        "id_sucursal": datos["id_sucursal"],
        "nombre": datos["nombre"],
        "capacidad": datos["capacidad"],
        "asientos_creados": datos["capacidad"]
    }

    return sala, None


# ============================================================
# PRUEBAS DE LISTADO DE SUCURSALES
# ============================================================

def test_lista_sucursales_activas_ordenadas(monkeypatch):
    esperado = [
        {
            "id_sucursal": 2,
            "nombre": "Centro",
            "direccion": "B"
        },
        {
            "id_sucursal": 1,
            "nombre": "Norte",
            "direccion": "A"
        }
    ]

    monkeypatch.setattr(
        sucursal_service,
        "listar_sucursales_activas",
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
        "listar_sucursales_activas",
        lambda: []
    )

    cliente = crear_cliente()
    respuesta = cliente.get("/api/sucursales")

    assert respuesta.status_code == 200
    assert respuesta.get_json()["data"] == []


# ============================================================
# PRUEBAS DE AUTENTICACION Y AUTORIZACION
# ============================================================

def test_salas_requiere_autenticacion():
    cliente = crear_cliente()

    respuesta = cliente.get("/api/sucursales/1/salas")

    assert respuesta.status_code == 401
    assert respuesta.get_json()["code"] == "NO_AUTENTICADO"


def test_salas_requiere_rol_admin():
    cliente = crear_cliente()

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 2
        sesion["rol"] = "EMPLEADO"
        sesion["nombre"] = "Empleado"

    respuesta = cliente.get("/api/sucursales/1/salas")

    assert respuesta.status_code == 403
    assert respuesta.get_json()["code"] == "PERMISOS_INSUFICIENTES"


def test_salas_rechaza_sesion_incompleta():
    cliente = crear_cliente()

    with cliente.session_transaction() as sesion:
        sesion["rol"] = "ADMIN"

    respuesta = cliente.get("/api/sucursales/1/salas")

    assert respuesta.status_code == 401
    assert respuesta.get_json()["code"] == "NO_AUTENTICADO"


def test_crear_sala_requiere_admin():
    cliente = crear_cliente()

    datos = {
        "id_sucursal": 1,
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post("/api/salas", json=datos)

    assert respuesta.status_code == 401

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 2
        sesion["rol"] = "EMPLEADO"
        sesion["nombre"] = "Empleado"

    respuesta = cliente.post("/api/salas", json=datos)

    assert respuesta.status_code == 403
    assert respuesta.get_json()["code"] == "PERMISOS_INSUFICIENTES"


# ============================================================
# PRUEBAS DE LISTADO DE SALAS
# ============================================================

def test_lista_salas_exitosa(monkeypatch):
    cliente = crear_cliente()
    sesion_admin(cliente)

    salas = [
        {
            "id_sala": 4,
            "id_sucursal": 1,
            "nombre": "Sala 1",
            "capacidad": 48,
            "estado": "ACTIVO"
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
    sesion_admin(cliente)

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
    sesion_admin(cliente)

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
        "id_sucursal": 1,
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post("/api/salas", json=datos)

    assert respuesta.status_code == 201
    assert respuesta.get_json()["status"] == "success"
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

    for capacidad in (0, 45, 201):
        datos = {
            "id_sucursal": 1,
            "nombre": "Sala 4",
            "capacidad": capacidad
        }

        respuesta = cliente.post("/api/salas", json=datos)

        assert respuesta.status_code == 400
        assert respuesta.get_json()["code"] == "DATOS_INVALIDOS"

    for capacidad in (46, 100, 200):
        datos = {
            "id_sucursal": 1,
            "nombre": "Sala 4",
            "capacidad": capacidad
        }

        respuesta = cliente.post("/api/salas", json=datos)

        assert respuesta.status_code == 201
        assert respuesta.get_json()["data"]["capacidad"] == capacidad


def test_crear_sala_rechaza_campos_desconocidos():
    cliente = crear_cliente()
    sesion_admin(cliente)

    datos = {
        "id_sucursal": 1,
        "nombre": "Sala 4",
        "capacidad": 48,
        "precio": 5000
    }

    respuesta = cliente.post("/api/salas", json=datos)

    assert respuesta.status_code == 400
    assert respuesta.get_json()["code"] == "DATOS_INVALIDOS"


@pytest.mark.parametrize(
    "datos",
    [
        {
            "id_sucursal": 1,
            "nombre": "Sala 4"
        },
        {
            "id_sucursal": 1,
            "nombre": "",
            "capacidad": 48
        },
        {
            "id_sucursal": 1,
            "nombre": "Sala 4",
            "capacidad": "48"
        },
        {
            "id_sucursal": 1,
            "nombre": "Sala 4",
            "capacidad": True
        },
        {
            "id_sucursal": True,
            "nombre": "Sala 4",
            "capacidad": 48
        },
        {
            "id_sucursal": -1,
            "nombre": "Sala 4",
            "capacidad": 48
        }
    ]
)
def test_crear_sala_rechaza_datos_invalidos(datos):
    cliente = crear_cliente()
    sesion_admin(cliente)

    respuesta = cliente.post("/api/salas", json=datos)

    assert respuesta.status_code == 400
    assert respuesta.get_json()["code"] == "DATOS_INVALIDOS"


def test_crear_sala_rechaza_json_invalido():
    cliente = crear_cliente()
    sesion_admin(cliente)

    respuesta = cliente.post(
        "/api/salas",
        json=["Sala 4", 48]
    )

    assert respuesta.status_code == 400
    assert respuesta.get_json()["code"] == "DATOS_INVALIDOS"


def test_crear_sala_sucursal_inexistente(monkeypatch):
    cliente = crear_cliente()
    sesion_admin(cliente)

    monkeypatch.setattr(
        sucursal_service,
        "crear_sala",
        lambda datos: (
            None,
            "SUCURSAL_NO_ENCONTRADA"
        )
    )

    datos = {
        "id_sucursal": 99,
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post("/api/salas", json=datos)

    assert respuesta.status_code == 404
    assert respuesta.get_json()["code"] == "SUCURSAL_NO_ENCONTRADA"


def test_crear_sala_duplicada(monkeypatch):
    cliente = crear_cliente()
    sesion_admin(cliente)

    monkeypatch.setattr(
        sucursal_service,
        "crear_sala",
        lambda datos: (
            None,
            "SALA_DUPLICADA"
        )
    )

    datos = {
        "id_sucursal": 1,
        "nombre": "Sala 4",
        "capacidad": 48
    }

    respuesta = cliente.post("/api/salas", json=datos)

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


# ============================================================
# PRUEBAS DE TRANSACCIONES DEL REPOSITORY
# ============================================================

def test_repositorio_confirma_transaccion_y_crea_asientos(monkeypatch):
    conexion = crear_conexion_falsa()

    monkeypatch.setattr(
        sucursal_repository,
        "get_db_connection",
        lambda: conexion
    )

    datos = {
        "id_sucursal": 1,
        "nombre": "Sala 4",
        "capacidad": 46
    }

    asientos = sucursal_service.generar_asientos(46)

    resultado = sucursal_repository.crear_sala_con_asientos(
        datos,
        asientos
    )

    conexion.start_transaction.assert_called_once()
    conexion.commit.assert_called_once()
    conexion.rollback.assert_not_called()

    cursor = conexion.cursor.return_value

    assert cursor.execute.call_count == 47
    assert resultado["asientos_creados"] == 46

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


def test_repositorio_revierte_si_falla_un_asiento(monkeypatch):
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
        "id_sucursal": 1,
        "nombre": "Sala 4",
        "capacidad": 46
    }

    asientos = sucursal_service.generar_asientos(46)

    with pytest.raises(Error):
        sucursal_repository.crear_sala_con_asientos(
            datos,
            asientos
        )

    conexion.start_transaction.assert_called_once()
    conexion.rollback.assert_called_once()
    conexion.commit.assert_not_called()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# PRUEBAS DE CONSULTAS DEL REPOSITORY
# ============================================================

def test_repositorio_sucursales_filtra_activas_y_ordena(monkeypatch):
    conexion = crear_conexion_falsa()

    filas = [
        {
            "id_sucursal": 2,
            "nombre": "Centro",
            "direccion": "B"
        }
    ]

    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = filas

    monkeypatch.setattr(
        sucursal_repository,
        "get_db_connection",
        lambda: conexion
    )

    resultado = sucursal_repository.listar_sucursales_activas()

    consulta = cursor.execute.call_args[0][0]

    assert resultado == filas
    assert "WHERE estado = 'ACTIVO'" in consulta
    assert "ORDER BY nombre ASC" in consulta

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()