from flask import Flask
from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Registrar el Blueprint de películas
    from app.routes.peliculas_routes import pelicula_bp

    app.register_blueprint(pelicula_bp)

    return app
