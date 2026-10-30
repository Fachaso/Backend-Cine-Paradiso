from flask import Blueprint

from app.controllers.auth_controller import login, logout, me, registro


auth_bp = Blueprint("auth", __name__, url_prefix="/api")

auth_bp.add_url_rule("/usuarios", view_func=registro, methods=["POST"])
auth_bp.add_url_rule("/sesiones", view_func=login, methods=["POST"])
auth_bp.add_url_rule("/sesiones", view_func=logout, methods=["DELETE"])
auth_bp.add_url_rule("/me", view_func=me, methods=["GET"])
