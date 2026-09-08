from flask import Flask
from .controller.cliente_controller import clientes_bp
from .controller.prato_controller import prato_bp
from .controller.pedido_controller import pedido_bp
from app.model.endereco import Endereco
from app.model.cliente import Cliente
from app.model.pedido import Pedido

# Aqui a gente registra todos ops Blueprints
def create_app():
    app = Flask(__name__)

    app.register_blueprint(clientes_bp)
    app.register_blueprint(prato_bp)
    app.register_blueprint(pedido_bp)

    return app