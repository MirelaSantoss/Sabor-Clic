import os

from flask import Flask

from app.db import criar_tabelas

from app.controller.cliente_controller import clientes_bp
from app.controller.prato_controller import prato_bp
from app.controller.pedido_controller import pedido_bp
from app.controller.admin_controller import admin_bp


def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Chave secreta utilizada para proteger as sessões.
    # Em produção, configure a variável de ambiente SECRET_KEY.
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "chave-temporaria-para-desenvolvimento"
    )

    # Configurações de segurança dos cookies.
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # False permite utilizar cookies em HTTP durante o desenvolvimento local.
    # Em produção, utilize HTTPS e altere para True.
    app.config["SESSION_COOKIE_SECURE"] = False

    # Tempo de duração da sessão.
    app.config["PERMANENT_SESSION_LIFETIME"] = 1800

    # Cria as tabelas do banco de dados.
    criar_tabelas()

    # Registra as rotas dos controllers.
    app.register_blueprint(clientes_bp)
    app.register_blueprint(prato_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(admin_bp)
    app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024

    return app
