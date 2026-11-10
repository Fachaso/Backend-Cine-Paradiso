from flask import Blueprint
from app.controllers.control_acceso_controller import usar_codigo_qr

control_acceso_bp = Blueprint("control_acceso", __name__, url_prefix="/api")
control_acceso_bp.add_url_rule(
    "/codigos-qr/<codigo_qr>",
    view_func=usar_codigo_qr,
    methods=["PATCH"]
)