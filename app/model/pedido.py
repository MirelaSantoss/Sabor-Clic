from app.db import conectar


class Pedido:

    @staticmethod
    def criar(cliente_id, itens):

        conexao = conectar()
        cursor = conexao.cursor()

        try:

            total = 0
            itens_validados = []

            # Confere os pratos e calcula o valor usando o banco.
            for item in itens:

                prato = cursor.execute("""
                    SELECT id, preco FROM pratos
                    WHERE id = ? AND ativo = 1
                """, (item["prato_id"],)).fetchone()

                quantidade = int(item["quantidade"])

                if prato is None or quantidade <= 0:
                    raise ValueError("Prato ou quantidade inválida.")

                preco = prato["preco"]
                total += preco * quantidade

                itens_validados.append((
                    prato["id"],
                    quantidade,
                    preco
                ))

            cursor.execute("""
                INSERT INTO pedidos (cliente_id, total)
                VALUES (?, ?)
            """, (cliente_id, total))

            pedido_id = cursor.lastrowid

            for prato_id, quantidade, preco in itens_validados:

                cursor.execute("""
                    INSERT INTO pedido_itens
                    (pedido_id, prato_id, quantidade, preco_unitario)
                    VALUES (?, ?, ?, ?)
                """, (pedido_id, prato_id, quantidade, preco))

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

        pedidos = conexao.execute("""
            SELECT pedidos.*, clientes.nome AS cliente_nome
            FROM pedidos
            INNER JOIN clientes
            ON pedidos.cliente_id = clientes.id
            ORDER BY pedidos.data_pedido DESC
        """).fetchall()

        conexao.close()

        return pedidos

    @staticmethod
    def listar_cliente(cliente_id):

        conexao = conectar()

        pedidos = conexao.execute("""
            SELECT * FROM pedidos
            WHERE cliente_id = ?
            ORDER BY data_pedido DESC
        """, (cliente_id,)).fetchall()

        conexao.close()

        return pedidos

    @staticmethod
    def atualizar_status(id_pedido, status):

        conexao = conectar()

        cursor = conexao.execute("""
            UPDATE pedidos
            SET status = ?
            WHERE id = ?
        """, (status, id_pedido))

        conexao.commit()
        alterados = cursor.rowcount
        conexao.close()

        return alterados
    @staticmethod
    def itens_do_pedido(pedido_id):
        conexao = conectar()
        try:
            itens = conexao.execute("""
                SELECT pratos.nome, pedido_itens.quantidade, pedido_itens.preco_unitario
                FROM pedido_itens JOIN pratos ON pratos.id = pedido_itens.prato_id
                WHERE pedido_itens.pedido_id = ?
            """, (pedido_id,)).fetchall()
            return [dict(item) for item in itens]
        finally:
            conexao.close()
