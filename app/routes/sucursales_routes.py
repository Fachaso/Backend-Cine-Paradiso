from flask import Blueprint

from app.controllers.sucursal_controller import crear_sala, listar_salas, listar_sucursales


sucursales_bp = Blueprint("sucursales", __name__, url_prefix="/api")

sucursales_bp.route("/sucursales", methods=["GET"])(listar_sucursales)
sucursales_bp.route("/sucursales/<int:id_sucursal>/salas", methods=["GET"])(listar_salas)
sucursales_bp.route("/salas", methods=["POST"])(crear_sala)
