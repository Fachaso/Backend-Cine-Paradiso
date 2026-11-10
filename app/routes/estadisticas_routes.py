from flask import Blueprint
from app.controllers.estadisticas_controller import (
    generar_reporte_pdf_controller,
    obtener_cancelaciones_controller,
    obtener_franjas_horarias_controller,
    obtener_ocupacion_controller,
    obtener_ventas_por_genero_controller,
)

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/api/estadisticas")


@estadisticas_bp.get("/ocupacion")
def get_ocupacion():
    return obtener_ocupacion_controller()


@estadisticas_bp.get("/ventas-por-genero")
def get_ventas_por_genero():
    return obtener_ventas_por_genero_controller()


@estadisticas_bp.get("/franjas-horarias")
def get_franjas_horarias():
    return obtener_franjas_horarias_controller()


@estadisticas_bp.get("/cancelaciones")
def get_cancelaciones():
    return obtener_cancelaciones_controller()
    
@estadisticas_bp.get("/reporte-pdf")
def get_reporte_pdf():
    return generar_reporte_pdf_controller()
