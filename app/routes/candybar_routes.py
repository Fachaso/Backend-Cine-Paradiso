from flask import Blueprint, request, jsonify

from app.services.candybar_service import crear_pedido_candybar


candybar_bp = Blueprint(
    "candybar",
    __name__,
    url_prefix="/api/candybar"
)


@candybar_bp.route("/pedidos", methods=["POST"])
def crear_pedido():
    datos = request.get_json(silent=True)

    resultado, codigo_http = crear_pedido_candybar(datos)

    return jsonify(resultado), codigo_http