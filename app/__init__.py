from flask import Flask
from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Importar los Blueprints implementados
    from app.routes.peliculas_routes import pelicula_bp
    from app.routes.candybar_routes import candybar_bp
    from app.routes.sucursales_routes import sucursales_bp

    # Registrar las rutas de películas
    app.register_blueprint(pelicula_bp)

    # Registrar las rutas del Candy Bar
    app.register_blueprint(candybar_bp)

    # Registrar las rutas de sucursales y salas
    app.register_blueprint(sucursales_bp)

    return app