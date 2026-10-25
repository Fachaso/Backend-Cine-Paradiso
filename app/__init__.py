from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Registro de Blueprints (se habilitan a medida que se implementen)
    from app.routes.auth_routes import auth_bp
    from app.routes.peliculas_routes import peliculas_bp
    from app.routes.compras_routes import compras_bp
    from app.routes.candybar_routes import candybar_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(peliculas_bp, url_prefix="/api/peliculas")
    app.register_blueprint(compras_bp, url_prefix="/api")
    app.register_blueprint(candybar_bp, url_prefix="/api/candybar")

    return app