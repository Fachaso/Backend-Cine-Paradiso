from flask import Blueprint

from app.controllers.servicio_controller import listar_servicios, obtener_servicio


servicios_bp = Blueprint("servicios", __name__, url_prefix="/api")

servicios_bp.route("/servicios", methods=["GET"])(listar_servicios)
servicios_bp.route("/servicios/<int:id_servicio>", methods=["GET"])(obtener_servicio)