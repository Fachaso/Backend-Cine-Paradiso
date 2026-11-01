from flask import Blueprint

from app.controllers.funcion_controller import (
    crear_funcion,
    listar_funciones,
    obtener_funcion_por_id,
)


funciones_bp = Blueprint("funciones", __name__, url_prefix="/api")

funciones_bp.route("/funciones", methods=["GET"])(listar_funciones)
funciones_bp.route("/funciones/<int:id_funcion>", methods=["GET"])(
    obtener_funcion_por_id
)
funciones_bp.route("/funciones", methods=["POST"])(crear_funcion)
