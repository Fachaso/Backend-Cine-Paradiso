import importlib.util
import os
from unittest.mock import patch
import pytest

# Carga dinámica del archivo app.py ubicado en la raíz para evitar conflicto de nombres con la carpeta /app
_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))
_spec = importlib.util.spec_from_file_location("main_app_module", _app_path)
_main_app_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_main_app_module)

flask_app = _main_app_module.app


@pytest.fixture
def client():
    """
    Cliente de pruebas de Flask configurado en modo TESTING.
    """
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test_secret_key'
    with flask_app.test_client() as client:
        yield client


def autenticar_cliente(client, rol="ADMIN", id_usuario=1):
    """
    Simula el inicio de sesión inyectando datos en la sesión de Flask.
    """
    with client.session_transaction() as sess:
        sess['id_usuario'] = id_usuario
        sess['rol'] = rol


class TestAccesoEstadisticas:
    """
    Pruebas de Control de Acceso y Autenticación (401 y 403).
    """

    @pytest.mark.parametrize("endpoint", [
        "/api/estadisticas/ocupacion",
        "/api/estadisticas/ventas-por-genero",
        "/api/estadisticas/franjas-horarias",
        "/api/estadisticas/cancelaciones",
        "/api/estadisticas/reporte-pdf",
    ])
    def test_acceso_sin_autenticacion_retorna_401(self, client, endpoint):
        response = client.get(endpoint)
        assert response.status_code == 401
        data = response.get_json()
        assert data["status"] == "error"
        assert data["code"] == "NO_AUTENTICADO"

    @pytest.mark.parametrize("endpoint", [
        "/api/estadisticas/ocupacion",
        "/api/estadisticas/ventas-por-genero",
        "/api/estadisticas/franjas-horarias",
        "/api/estadisticas/cancelaciones",
        "/api/estadisticas/reporte-pdf",
    ])
    def test_acceso_rol_cliente_retorna_403(self, client, endpoint):
        autenticar_cliente(client, rol="CLIENTE")
        response = client.get(endpoint)
        assert response.status_code == 403
        data = response.get_json()
        assert data["status"] == "error"
        assert data["code"] == "ACCESO_DENEGADO"


class TestEndpointsEstadisticasAdmin:
    """
    Pruebas de respuesta exitosa (HTTP 200) para el rol ADMIN.
    """

    @patch("app.services.estadisticas_service.obtener_ocupacion_db")
    def test_obtener_ocupacion_exito(self, mock_db, client):
        autenticar_cliente(client, rol="ADMIN")
        mock_db.return_value = [{
            "id_funcion": 1,
            "titulo_pelicula": "Gladiator II",
            "nombre_sala": "Sala 1",
            "fecha_hora": "2026-11-05T20:00:00",
            "capacidad": 100,
            "entradas_vendidas": 50
        }]

        response = client.get("/api/estadisticas/ocupacion")
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["status"] == "success"
        assert len(json_data["data"]) == 1
        assert json_data["data"][0]["porcentaje_ocupacion"] == 50.0

    @patch("app.services.estadisticas_service.obtener_ventas_por_genero_db")
    def test_obtener_ventas_por_genero_exito(self, mock_db, client):
        autenticar_cliente(client, rol="ADMIN")
        mock_db.return_value = [{
            "genero": "Acción",
            "total_ventas": 15000.00,
            "entradas_vendidas": 10
        }]

        response = client.get("/api/estadisticas/ventas-por-genero")
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["status"] == "success"
        assert json_data["data"][0]["genero"] == "Acción"

    @patch("app.services.estadisticas_service.obtener_franjas_horarias_db")
    def test_obtener_franjas_horarias_exito(self, mock_db, client):
        autenticar_cliente(client, rol="ADMIN")
        mock_db.return_value = [{
            "hora": "20:00",
            "entradas_vendidas": 25
        }]

        response = client.get("/api/estadisticas/franjas-horarias")
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["status"] == "success"
        assert json_data["data"][0]["hora"] == "20:00"

    @patch("app.services.estadisticas_service.obtener_cancelaciones_db")
    def test_obtener_cancelaciones_exito(self, mock_db, client):
        autenticar_cliente(client, rol="ADMIN")
        mock_db.return_value = 3

        response = client.get("/api/estadisticas/cancelaciones")
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["status"] == "success"
        assert json_data["data"]["total_cancelaciones"] == 3

    @patch("app.services.estadisticas_service.obtener_cancelaciones_db")
    @patch("app.services.estadisticas_service.obtener_peliculas_mas_vistas_db")
    @patch("app.services.estadisticas_service.obtener_ventas_por_genero_db")
    def test_generar_reporte_pdf_exito(self, mock_genero, mock_pelis, mock_canc, client):
        autenticar_cliente(client, rol="ADMIN")
        mock_canc.return_value = 2
        mock_pelis.return_value = []
        mock_genero.return_value = []

        response = client.get("/api/estadisticas/reporte-pdf")
        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert "attachment; filename=reporte_estadisticas.pdf" in response.headers["Content-Disposition"]
        assert response.data.startswith(b"%PDF")
