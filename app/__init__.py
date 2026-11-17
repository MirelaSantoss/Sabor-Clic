import os
from pathlib import Path

from flask import Flask, jsonify

from app.db import criar_tabelas

from app.controller.cliente_controller import clientes_bp
from app.controller.prato_controller import prato_bp
from app.controller.pedido_controller import pedido_bp
from app.controller.admin_controller import admin_bp


def _carregar_env():
    caminho_env = Path(__file__).resolve().parent.parent / ".env"
    if not caminho_env.exists():
        return
    for linha in caminho_env.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip())


def create_app():
    _carregar_env()

    app = Flask(__name__, template_folder='views')

    app = Flask(
        __name__,
        template_folder="views",
        static_folder="static"
    )

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "chave-temporaria-para-desenvolvimento"
    )

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("COOKIE_SECURE", "0") == "1"
    app.config["PERMANENT_SESSION_LIFETIME"] = 1800
    app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024

    @app.errorhandler(413)
    def arquivo_muito_grande(_erro):
        return jsonify({"erro": "O arquivo enviado excede o limite máximo de 3 MB."}), 413

    criar_tabelas()

    app.register_blueprint(clientes_bp)
    app.register_blueprint(prato_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(admin_bp)

    return app
