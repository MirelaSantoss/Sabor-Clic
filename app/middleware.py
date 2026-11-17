import math
import re
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request

PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PADRAO_TAGS_HTML = re.compile(r"<[^>]*>")
CATEGORIAS_VALIDAS = ("Pratos", "Bebidas", "Combos", "Sobremesas")


def limpar_texto(valor):
    if valor is None:
        return ""
    return PADRAO_TAGS_HTML.sub("", str(valor)).strip()


def email_valido(email):
    if not isinstance(email, str):
        return False
    email_limpo = email.strip()
    return 3 <= len(email_limpo) <= 120 and bool(PADRAO_EMAIL.match(email_limpo))


def senha_valida(senha):
    if not isinstance(senha, str) or len(senha) < 8:
        return False
    tem_letra = any(c.isalpha() for c in senha)
    tem_numero = any(c.isdigit() for c in senha)
    return tem_letra and tem_numero


def nome_prato_valido(nome):
    nome_limpo = limpar_texto(nome)
    return 3 <= len(nome_limpo) <= 120


def converter_preco(valor):
    if isinstance(valor, bool) or valor is None:
        raise ValueError("Preço inválido.")
    texto = str(valor).strip().replace(",", ".")
    preco = float(texto)
    if math.isnan(preco) or math.isinf(preco) or preco <= 0:
        raise ValueError("O preço deve ser maior que zero.")
    return round(preco, 2)


def converter_ativo(valor, padrao=1):
    if valor is None:
        return int(bool(padrao))
    if isinstance(valor, bool):
        return 1 if valor else 0
    if isinstance(valor, (int, float)):
        return 1 if valor != 0 else 0
    texto = str(valor).strip().lower()
    if texto in ("0", "false", "nao", "não", "inativo", "off", ""):
        return 0
    return 1


def _eh_requisicao_api():
    return (
        request.is_json
        or request.path.startswith("/api/")
        or request.path.startswith("/pedidos")
        or request.path == "/minha-conta"
    )


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
