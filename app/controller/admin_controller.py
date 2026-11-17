import uuid
from pathlib import Path
from flask import Blueprint, render_template, jsonify, request, current_app, session
from werkzeug.utils import secure_filename
from app.middleware import (
    permissao_obrigatoria,
    limpar_texto,
    nome_prato_valido,
    converter_preco,
    converter_ativo,
    CATEGORIAS_VALIDAS
)
from app.model.prato import Prato
from app.model.cliente import Cliente
from app.model.pedido import Pedido
from app.model.bancada import Bancada

admin_bp = Blueprint("admin", __name__)
EXTENSOES = {"jpg", "jpeg", "png", "webp"}


def salvar_foto(arquivo):
    if not arquivo or not arquivo.filename:
        return None
    nome = secure_filename(arquivo.filename)
    if "." not in nome or nome.rsplit(".", 1)[-1].lower() not in EXTENSOES:
        raise ValueError("Envie uma foto JPG, PNG ou WEBP.")
    pasta = Path(current_app.static_folder) / "uploads"
    pasta.mkdir(exist_ok=True)
    novo_nome = uuid.uuid4().hex + "." + nome.rsplit(".", 1)[-1].lower()
    arquivo.save(pasta / novo_nome)
    return "uploads/" + novo_nome


@admin_bp.route("/admin")
@permissao_obrigatoria("administrador")
def painel():
    return render_template("admin.html")


@admin_bp.route("/api/admin/pratos", methods=["GET", "POST"])
@permissao_obrigatoria("administrador")
def pratos():
    if request.method == "GET":
        return jsonify(Prato.listar_todos())
    try:
        dados = request.form if request.form else (request.get_json(silent=True) or {})
        nome = limpar_texto(dados.get("nome", ""))
        descricao = limpar_texto(dados.get("descricao", ""))
        preco = converter_preco(dados.get("preco"))
        categoria = limpar_texto(dados.get("categoria", "Pratos")) or "Pratos"
        tempo_preparo_min = int(dados.get("tempo_preparo_min") or 20)
        estoque = int(dados.get("estoque") if dados.get("estoque") not in (None, "") else 50)
        if not nome_prato_valido(nome):
            raise ValueError("O nome do prato deve ter entre 3 e 120 caracteres.")
        if not descricao or categoria not in CATEGORIAS_VALIDAS or tempo_preparo_min < 1 or estoque < 0:
            raise ValueError("Confira os dados do produto.")
        imagem = salvar_foto(request.files.get("imagem")) if request.files else None
        novo = Prato.cadastrar(nome, descricao, preco, categoria, imagem, tempo_preparo_min, estoque)
        return jsonify({"id": novo, "mensagem": "Produto cadastrado!"}), 201
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/pratos/<int:id>", methods=["PUT", "POST", "DELETE"])
@permissao_obrigatoria("administrador")
def editar_prato(id):
    prato = Prato.buscar(id)
    if not prato:
        return jsonify({"erro": "Produto não encontrado"}), 404
    if request.method == "DELETE":
        Prato.excluir(id)
        return jsonify({"mensagem": "Produto desativado"})
    dados = request.form if request.form else (request.get_json(silent=True) or {})
    try:
        nome = limpar_texto(dados.get("nome", prato["nome"]))
        descricao = limpar_texto(dados.get("descricao", prato["descricao"]))
        preco = converter_preco(dados.get("preco", prato["preco"]))
        categoria = limpar_texto(dados.get("categoria", prato["categoria"])) or prato["categoria"]
        ativo = converter_ativo(dados.get("ativo"), prato["ativo"])
        tempo_preparo = int(dados.get("tempo_preparo_min", prato["tempo_preparo_min"] or 20))
        estoque = int(dados.get("estoque", prato["estoque"]))
        remover_img = bool(converter_ativo(dados.get("remover_imagem"), 0))
        if not nome_prato_valido(nome):
            raise ValueError("O nome do prato deve ter entre 3 e 120 caracteres.")
        if not descricao or categoria not in CATEGORIAS_VALIDAS or tempo_preparo < 1 or estoque < 0:
            raise ValueError("Dados inválidos")
        imagem = salvar_foto(request.files.get("imagem")) if request.files else None
        Prato.atualizar(
            id,
            nome,
            descricao,
            preco,
            ativo,
            categoria,
            imagem,
            tempo_preparo,
            estoque,
            remover_imagem=remover_img and imagem is None
        )
        return jsonify({"mensagem": "Produto atualizado com sucesso!"})
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/pratos/<int:id>/estoque", methods=["PUT"])
@permissao_obrigatoria("administrador")
def atualizar_estoque_prato(id):
    prato = Prato.buscar(id)
    if not prato:
        return jsonify({"erro": "Produto não encontrado."}), 404
    dados = request.get_json(silent=True) or {}
    try:
        nova_qtd = int(dados.get("estoque"))
        if isinstance(dados.get("estoque"), bool) or nova_qtd < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")
        Prato.atualizar_estoque(id, nova_qtd)
        return jsonify({"mensagem": f"Estoque de '{prato['nome']}' atualizado para {nova_qtd} un.", "estoque": nova_qtd}), 200
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro) or "Quantidade inválida."}), 400


@admin_bp.route("/api/admin/funcionarios", methods=["POST"])
@permissao_obrigatoria("administrador")
def cadastrar_funcionario():
    dados = request.get_json(silent=True) or {}
    try:
        novo_id = Cliente.cadastrar_funcionario(
            dados.get("nome", ""),
            dados.get("email", ""),
            dados.get("senha", ""),
            dados.get("tipo", ""),
            dados.get("telefone")
        )
        return jsonify({"id": novo_id, "mensagem": "Funcionário cadastrado com sucesso!"}), 201
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/funcionarios/<int:id>", methods=["PUT", "DELETE"])
@permissao_obrigatoria("administrador")
def editar_ou_remover_funcionario(id):
    try:
        if request.method == "DELETE":
            alterados = Cliente.remover_funcionario(id, session.get("usuario_id"))
            if not alterados:
                return jsonify({"erro": "Funcionário não encontrado."}), 404
            return jsonify({"mensagem": "Funcionário removido com sucesso!"}), 200

        dados = request.get_json(silent=True) or {}
        alterados = Cliente.atualizar_funcionario(
            id,
            dados.get("nome", ""),
            dados.get("email", ""),
            dados.get("tipo", ""),
            dados.get("telefone"),
            dados.get("nova_senha")
        )
        if not alterados:
            return jsonify({"erro": "Funcionário não encontrado."}), 404
        return jsonify({"mensagem": "Dados do funcionário atualizados com sucesso!"}), 200
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/clientes", methods=["GET"])
@permissao_obrigatoria("administrador")
def listar_clientes_admin():
    return jsonify(Cliente.listar_clientes()), 200


@admin_bp.route("/api/admin/clientes/<int:id>", methods=["PUT"])
@permissao_obrigatoria("administrador")
def editar_cliente_admin(id):
    dados = request.get_json(silent=True) or {}
    try:
        alterados = Cliente.atualizar_cliente_admin(id, dados)
        if not alterados:
            return jsonify({"erro": "Cliente não encontrado."}), 404
        return jsonify({"mensagem": "Cadastro do cliente atualizado com sucesso!"}), 200
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/pedidos/<int:id>", methods=["PUT"])
@permissao_obrigatoria("administrador")
def editar_pedido_admin(id):
    dados = request.get_json(silent=True) or {}
    try:
        alterados = Pedido.atualizar_pedido_admin(
            id,
            dados.get("status", ""),
            dados.get("tempo_estimado"),
            dados.get("observacoes")
        )
        if not alterados:
            return jsonify({"erro": "Pedido não encontrado."}), 404
        return jsonify({"mensagem": f"Pedido #{id} atualizado com sucesso!"}), 200
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/historico-status", methods=["GET"])
@permissao_obrigatoria("administrador")
def listar_historico_status_admin():
    return jsonify(Pedido.listar_historico_status()), 200


@admin_bp.route("/api/admin/relatorio")
@permissao_obrigatoria("administrador")
def relatorio():
    resumo = Pedido.resumo_vendas()
    prod_bancadas = Bancada.produtividade()
    receita_bancadas = round(sum(float(b["receita_total_gerada"]) for b in prod_bancadas), 2)
    resumo["receita_bancadas"] = receita_bancadas
    resumo["faturamento_global"] = round(float(resumo.get("faturamento", 0)) + receita_bancadas, 2)
    resumo["produtividade_bancadas"] = prod_bancadas
    resumo["alertas_estoque"] = Prato.alertas_estoque(limite=10)
    resumo["funcionarios"] = Cliente.listar_funcionarios()
    resumo["clientes"] = Cliente.listar_clientes()
    resumo["bancadas"] = Bancada.listar()
    resumo["reservas_bancadas"] = Bancada.listar_reservas()
    resumo["historico_status"] = Pedido.listar_historico_status()
    return jsonify(resumo)


@admin_bp.route("/api/bancadas", methods=["POST"])
@admin_bp.route("/api/admin/bancadas", methods=["POST"])
@permissao_obrigatoria("administrador")
def cadastrar_bancada():
    dados = request.get_json(silent=True) or {}
    try:
        novo_id = Bancada.cadastrar(
            dados.get("cod_identificacao", ""),
            dados.get("descricao", ""),
            dados.get("valor_hora"),
            dados.get("valor_caucao", 0),
            dados.get("status_operacional", "DISPONIVEL")
        )
        return jsonify({"id": novo_id, "mensagem": "Bancada cadastrada com sucesso!"}), 201
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/bancadas/<int:id>", methods=["PUT"])
@admin_bp.route("/api/admin/bancadas/<int:id>", methods=["PUT"])
@permissao_obrigatoria("administrador")
def atualizar_bancada(id):
    dados = request.get_json(silent=True) or {}
    try:
        bancada = Bancada.buscar(id)
        if not bancada:
            return jsonify({"erro": "Bancada não encontrada."}), 404
        Bancada.atualizar(
            id,
            dados.get("valor_hora", bancada["valor_hora"]),
            dados.get("valor_caucao", bancada["valor_caucao"]),
            dados.get("descricao", bancada["descricao"]),
            dados.get("status_operacional", bancada["status_operacional"]),
            dados.get("cod_identificacao", bancada["cod_identificacao"])
        )
        return jsonify({"mensagem": "Bancada atualizada com sucesso."}), 200
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/reservas/<int:id>", methods=["PUT"])
@permissao_obrigatoria("administrador")
def editar_reserva_bancada_admin(id):
    dados = request.get_json(silent=True) or {}
    try:
        reserva = Bancada.buscar_reserva(id)
        if not reserva:
            return jsonify({"erro": "Reserva não encontrada."}), 404
        Bancada.atualizar_reserva_admin(
            id,
            bancada_id=dados.get("bancada_id", dados.get("id_bancada")),
            data_hora_inicio=dados.get("data_hora_inicio"),
            data_hora_fim=dados.get("data_hora_fim"),
            status_reserva=dados.get("status_reserva"),
            valor_adicionais=dados.get("valor_adicionais")
        )
        return jsonify({"mensagem": "Reserva atualizada com sucesso!"}), 200
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400
