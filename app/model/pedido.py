from app.db import conectar
from app.middleware import limpar_texto

STATUS_PEDIDO_VALIDOS = (
    "Aguardando",
    "Iniciando Preparo",
    "Pronto para Entrega",
    "Entregue",
    "Cancelado"
)


def _converter_quantidade_inteira(valor):
    if isinstance(valor, bool) or valor is None:
        raise ValueError("Quantidade inválida.")
    if isinstance(valor, int):
        qtd = valor
    elif isinstance(valor, float):
        if not valor.is_integer():
            raise ValueError("Quantidade deve ser inteira.")
        qtd = int(valor)
    elif isinstance(valor, str):
        texto = valor.strip()
        if not texto.isdigit():
            raise ValueError("Quantidade inválida.")
        qtd = int(texto)
    else:
        raise ValueError("Quantidade inválida.")

    if qtd < 1:
        raise ValueError("Quantidade mínima é 1.")
    return qtd


class Pedido:

    @staticmethod
    def criar(cliente_id, itens, observacoes_gerais=None):
        conexao = conectar()
        cursor = conexao.cursor()

        try:
            total = 0.0
            maior_tempo = 20
            itens_validados = []
            observacoes_coletadas = []

            if observacoes_gerais:
                obs_geral_limpa = limpar_texto(observacoes_gerais)[:255]
                if obs_geral_limpa:
                    observacoes_coletadas.append(obs_geral_limpa)

            for item in itens:
                if not isinstance(item, dict):
                    raise ValueError("Formato de item inválido.")

                prato_id = item.get("prato_id", item.get("id"))
                if isinstance(prato_id, bool) or prato_id is None:
                    raise ValueError("Prato inválido.")
                prato_id = int(prato_id)

                quantidade = _converter_quantidade_inteira(item.get("quantidade"))
                obs_item = limpar_texto(item.get("observacoes", ""))[:255] or None

                prato = cursor.execute("""
                    SELECT id, nome, preco, COALESCE(tempo_preparo_min, 20) AS tempo_preparo_min
                    FROM pratos
                    WHERE id = ? AND ativo = 1
                """, (prato_id,)).fetchone()

                if prato is None:
                    raise ValueError("Prato indisponível ou inexistente.")

                preco = float(prato["preco"])
                total += preco * quantidade
                if int(prato["tempo_preparo_min"]) > maior_tempo:
                    maior_tempo = int(prato["tempo_preparo_min"])

                if obs_item:
                    observacoes_coletadas.append(f"{prato['nome']}: {obs_item}")

                itens_validados.append((
                    prato["id"],
                    quantidade,
                    preco,
                    obs_item
                ))

            resumo_observacoes = " | ".join(observacoes_coletadas)[:255] if observacoes_coletadas else None

            cursor.execute("""
                INSERT INTO pedidos (cliente_id, total, tempo_estimado, observacoes)
                VALUES (?, ?, ?, ?)
            """, (cliente_id, round(total, 2), maior_tempo, resumo_observacoes))

            pedido_id = cursor.lastrowid

            for prato_id, quantidade, preco, obs_item in itens_validados:
                cursor.execute("""
                    INSERT INTO pedido_itens
                    (pedido_id, prato_id, quantidade, preco_unitario, observacoes)
                    VALUES (?, ?, ?, ?, ?)
                """, (pedido_id, prato_id, quantidade, preco, obs_item))

            conexao.commit()
            return pedido_id

        except Exception:
            conexao.rollback()
            raise

        finally:
            conexao.close()

    @staticmethod
    def listar():
        conexao = conectar()
        try:
            pedidos = conexao.execute("""
                SELECT pedidos.*, clientes.nome AS cliente_nome
                FROM pedidos
                INNER JOIN clientes
                ON pedidos.cliente_id = clientes.id
                ORDER BY
                    CASE pedidos.status
                        WHEN 'Aguardando' THEN 1
                        WHEN 'Iniciando Preparo' THEN 2
                        WHEN 'Pronto para Entrega' THEN 3
                        WHEN 'Entregue' THEN 4
                        ELSE 5
                    END,
                    pedidos.data_pedido ASC,
                    pedidos.id ASC
            """).fetchall()
            return pedidos
        finally:
            conexao.close()

    @staticmethod
    def listar_cliente(cliente_id):
        conexao = conectar()
        try:
            pedidos = conexao.execute("""
                SELECT * FROM pedidos
                WHERE cliente_id = ?
                ORDER BY data_pedido DESC, id DESC
            """, (cliente_id,)).fetchall()
            return pedidos
        finally:
            conexao.close()

    @staticmethod
    def atualizar_status(id_pedido, status):
        if status not in STATUS_PEDIDO_VALIDOS:
            raise ValueError("Status inválido.")
        conexao = conectar()
        try:
            cursor = conexao.execute("""
                UPDATE pedidos
                SET status = ?
                WHERE id = ?
            """, (status, id_pedido))

            conexao.commit()
            return cursor.rowcount
        finally:
            conexao.close()

    @staticmethod
    def definir_tempo(id_pedido, minutos, observacoes=None):
        conexao = conectar()
        try:
            if observacoes is not None:
                obs_limpa = limpar_texto(observacoes)[:255] or None
                cursor = conexao.execute(
                    "UPDATE pedidos SET tempo_estimado = ?, observacoes = ? WHERE id = ?",
                    (minutos, obs_limpa, id_pedido)
                )
            else:
                cursor = conexao.execute(
                    "UPDATE pedidos SET tempo_estimado = ? WHERE id = ?",
                    (minutos, id_pedido)
                )
            conexao.commit()
            return cursor.rowcount
        finally:
            conexao.close()

    @staticmethod
    def atualizar_pedido_admin(id_pedido, status, tempo_estimado=None, observacoes=None):
        if status not in STATUS_PEDIDO_VALIDOS:
            raise ValueError("Status de pedido inválido.")

        tempo_final = None
        if tempo_estimado not in (None, ""):
            if isinstance(tempo_estimado, bool):
                raise ValueError("Tempo estimado inválido.")
            tempo_final = int(tempo_estimado)
            if tempo_final < 1 or tempo_final > 480:
                raise ValueError("O tempo estimado deve ficar entre 1 e 480 minutos.")

        obs_final = limpar_texto(observacoes)[:255] if observacoes is not None else None

        conexao = conectar()
        try:
            atual = conexao.execute("SELECT * FROM pedidos WHERE id = ?", (id_pedido,)).fetchone()
            if atual is None:
                return 0

            conexao.execute("""
                UPDATE pedidos
                SET
                    status = ?,
                    tempo_estimado = COALESCE(?, tempo_estimado),
                    observacoes = ?
                WHERE id = ?
            """, (
                status,
                tempo_final,
                obs_final if observacoes is not None else atual["observacoes"],
                id_pedido
            ))
            conexao.commit()
            return 1
        finally:
            conexao.close()

    @staticmethod
    def listar_historico_status(limite=50):
        conexao = conectar()
        try:
            linhas = conexao.execute("""
                SELECT
                    h.id,
                    h.pedido_id,
                    h.status,
                    h.alterado_em,
                    c.nome AS cliente_nome
                FROM historico_status h
                JOIN pedidos p ON p.id = h.pedido_id
                JOIN clientes c ON c.id = p.cliente_id
                ORDER BY h.id DESC
                LIMIT ?
            """, (int(limite),)).fetchall()
            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()

    @staticmethod
    def itens_do_pedido(pedido_id):
        conexao = conectar()
        try:
            itens = conexao.execute("""
                SELECT
                    pratos.id AS prato_id,
                    pratos.nome,
                    COALESCE(pratos.categoria, 'Pratos') AS categoria,
                    pedido_itens.quantidade,
                    pedido_itens.preco_unitario,
                    pedido_itens.observacoes
                FROM pedido_itens
                JOIN pratos ON pratos.id = pedido_itens.prato_id
                WHERE pedido_itens.pedido_id = ?
            """, (pedido_id,)).fetchall()
            return [dict(item) for item in itens]
        finally:
            conexao.close()

    @staticmethod
    def resumo_vendas():
        conexao = conectar()
        try:
            linha = conexao.execute("""
                SELECT
                    COUNT(*) AS pedidos,
                    ROUND(COALESCE(SUM(total), 0), 2) AS faturamento,
                    ROUND(COALESCE(AVG(total), 0), 2) AS ticket_medio
                FROM pedidos
                WHERE status <> 'Cancelado'
            """).fetchone()

            resumo = dict(linha)

            por_status = conexao.execute("""
                SELECT status, COUNT(*) AS quantidade
                FROM pedidos
                GROUP BY status
                ORDER BY quantidade DESC
            """).fetchall()
            resumo["por_status"] = [dict(s) for s in por_status]

            ranking = conexao.execute("""
                SELECT
                    p.id,
                    p.nome,
                    p.categoria,
                    p.preco,
                    COALESCE(SUM(CASE WHEN ped.status <> 'Cancelado' THEN i.quantidade ELSE 0 END), 0) AS unidades_vendidas,
                    ROUND(COALESCE(SUM(CASE WHEN ped.status <> 'Cancelado' THEN i.quantidade * i.preco_unitario ELSE 0 END), 0), 2) AS receita_prato
                FROM pratos p
                LEFT JOIN pedido_itens i ON i.prato_id = p.id
                LEFT JOIN pedidos ped ON ped.id = i.pedido_id
                GROUP BY p.id
                ORDER BY unidades_vendidas DESC, receita_prato DESC, p.nome ASC
            """).fetchall()
            resumo["ranking_pratos"] = [dict(r) for r in ranking]

            return resumo
        finally:
            conexao.close()
