from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request

#diferenciar as chamadas de dados do json
def _eh_requisicao_api():
    return (
        request.is_json
        or request.path.startswith("/api/")
        or request.path.startswith("/pedidos")
        or request.path == "/minha-conta"
    )

#verificação de etiqueta do usuario
def _destino_padrao(tipo):
    rotas = {
        "administrador": "admin.painel",
        "cozinheiro": "pedido_controller.pagina_cozinheiro",
        "cliente": "prato.pagina_cardapio",
    }
    destino = rotas.get(tipo, "prato.inicio")
    return url_for(destino)


def login_obrigatorio(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            if _eh_requisicao_api():
                return jsonify({"erro": "É necessário fazer login."}), 401

            flash("Faça login para acessar esta página.", "erro")
            return redirect(url_for("cliente.pagina_login"))

        return funcao(*args, **kwargs)

    return verificar


def permissao_obrigatoria(*tipos_permitidos):
    def decorador(funcao):
        @wraps(funcao)
        def verificar(*args, **kwargs):
            if "usuario_id" not in session:
                if _eh_requisicao_api():
                    return jsonify({"erro": "Usuário não autenticado."}), 401

                flash("Faça login para acessar esta página.", "erro")
                return redirect(url_for("cliente.pagina_login"))

            tipo_atual = session.get("tipo")
            if tipo_atual not in tipos_permitidos:
                if _eh_requisicao_api():
                    return jsonify({"erro": "Você não possui permissão para esta ação."}), 403

                flash("Você não tem permissão para acessar esta área.", "erro")
                return redirect(_destino_padrao(tipo_atual))

            return funcao(*args, **kwargs)

        return verificar

    return decorador