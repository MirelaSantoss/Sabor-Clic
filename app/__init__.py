from flask import Flask
from .controller.cliente_controller import clientes_bp
from .controller.prato_controller import prato_bp

# Aqui a gente registra todos ops Blueprints
def create_app():
    app = Flask(__name__)

    app.register_blueprint(clientes_bp)
    app.register_blueprint(prato_bp)

    return app