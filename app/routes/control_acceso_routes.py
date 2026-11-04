from flask import Blueprint

from app.controllers.control_acceso_controller import validar_qr_ingreso

control_acceso_bp = Blueprint("control_acceso", __name__, url_prefix="/api")

control_acceso_bp.route("/codigos-qr/<codigo_qr>", methods=["PATCH"])(validar_qr_ingreso)

