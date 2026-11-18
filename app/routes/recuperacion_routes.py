from flask import Blueprint

from app.controllers.recuperacion_controller import (
    restablecer_password,
    solicitar_recuperacion,
)

recuperacion_bp = Blueprint("recuperacion", __name__, url_prefix="/api")

recuperacion_bp.add_url_rule(
    "/recuperar-password", view_func=solicitar_recuperacion, methods=["POST"]
)
recuperacion_bp.add_url_rule(
    "/restablecer-password", view_func=restablecer_password, methods=["POST"]
)