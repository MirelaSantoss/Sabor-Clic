from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request


def login_obrigatorio(funcao):
    """Impede o acesso de usuários que não fizeram login."""

    @wraps(funcao)
    def verificar(*args, **kwargs):

        if "usuario_id" not in session:

            if request.is_json or request.path.startswith("/pedidos") or request.path.startswith("/api/"):
                return jsonify({
                    "erro": "É necessário fazer login."
                }), 401

            flash("Faça login para acessar esta página.", "erro")
            return redirect(url_for("cliente.pagina_login"))

        return funcao(*args, **kwargs)

    return verificar


def permissao_obrigatoria(*tipos_permitidos):
    """Permite o acesso somente aos tipos de usuário autorizados."""

    def decorador(funcao):

        @wraps(funcao)
        def verificar(*args, **kwargs):

            if "usuario_id" not in session:
                if request.method == "GET" and request.path == "/cozinheiro":
                    flash("Entre como administrador para acessar a cozinha.", "erro")
                    return redirect(url_for("cliente.pagina_login_tipo", modo="cozinheiro"))
                return jsonify({"erro": "Usuário não autenticado."}), 401

            if session.get("tipo") not in tipos_permitidos:
                if request.method == "GET" and request.path == "/cozinheiro":
                    flash("Sua conta não tem permissão para acessar a cozinha.", "erro")
                    return redirect(url_for("cliente.pagina_login"))
                return jsonify({"erro": "Você não possui permissão para esta ação."}), 403

            return funcao(*args, **kwargs)

        return verificar

    return decorador