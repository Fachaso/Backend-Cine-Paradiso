from flask import Blueprint

from app.controllers.servicio_controller import listar_servicios


servicios_bp = Blueprint("servicios", __name__, url_prefix="/api")

servicios_bp.route("/servicios", methods=["GET"])(listar_servicios)