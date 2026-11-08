import os

from flask import Flask

from app.db import criar_tabelas

from app.controller.cliente_controller import clientes_bp
from app.controller.prato_controller import prato_bp
from app.controller.pedido_controller import pedido_bp


def create_app():

    app = Flask(__name__, template_folder="templates",
                static_folder="static")

    # Chave utilizada para proteger as sessões
    app.secret_key = os.environ.get(
        "SECRET_KEY",
        "chave-local-sabor-clic-trocar-em-producao"
    )

    # Configurações dos cookies
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False

    # Criação das tabelas
    criar_tabelas()

    # Registro dos controladores
    app.register_blueprint(clientes_bp)
    app.register_blueprint(prato_bp)
    app.register_blueprint(pedido_bp)

    return app