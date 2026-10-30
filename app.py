import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Carga de variables de entorno desde .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

    # Habilitar CORS para permitir solicitudes del Frontend
    CORS(app)

    # Registros de Blueprints (Rutas implementadas)
    from app.routes.peliculas_routes import pelicula_bp
    from app.routes.candybar_routes import candybar_bp
    from app.routes.sucursales_routes import sucursales_bp

    app.register_blueprint(pelicula_bp)
    app.register_blueprint(candybar_bp)
    app.register_blueprint(sucursales_bp)

    # Route de chequeo de salud
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "success",
            "message": "Backend Cine Paradiso activo y funcionando correctamente"
        }), 200

    # -------------------------------------------------------------------
    # MANEJO GLOBAL DE ERRORES EN FORMATO JSON
    # -------------------------------------------------------------------
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "status": "error",
            "message": "Petición no válida (Bad Request)"
        }), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            "status": "error",
            "message": "No autorizado (Requiere autenticación)"
        }), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            "status": "error",
            "message": "Acceso prohibido (Permisos insuficientes)"
        }), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "status": "error",
            "message": "Recurso no encontrado"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return jsonify({
            "status": "error",
            "message": "Método HTTP no permitido para esta ruta"
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor"
        }), 500

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
