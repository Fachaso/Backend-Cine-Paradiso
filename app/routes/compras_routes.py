from flask import Blueprint

from app.controllers.compras_controller import (
    actualizar_compra,
    crear_compra,
    obtener_compra,
)


compras_bp = Blueprint("compras", __name__, url_prefix="/api")
compras_bp.add_url_rule("/compras", view_func=crear_compra, methods=["POST"])
compras_bp.add_url_rule(
    "/compras/<int:id_compra>",
    view_func=actualizar_compra,
    methods=["PATCH"]
)
compras_bp.add_url_rule(
    "/compras/<int:id_compra>",
    view_func=obtener_compra,
    methods=["GET"]
)
