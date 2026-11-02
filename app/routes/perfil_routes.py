from flask import Blueprint

from app.controllers.perfil_controller import consultar_perfil

perfil_bp = Blueprint("perfil", __name__, url_prefix="/api")

perfil_bp.add_url_rule("/perfil", view_func=consultar_perfil, methods=["GET"])