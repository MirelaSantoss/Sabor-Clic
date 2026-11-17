from app.db import conectar


class Prato:

    @staticmethod
    def listar():
        conexao = conectar()
        try:
            pratos = conexao.execute("""
                SELECT
                    pratos.*,
                    COALESCE(estoque_pratos.quantidade, 50) AS estoque
                FROM pratos
                LEFT JOIN estoque_pratos ON estoque_pratos.prato_id = pratos.id
                WHERE pratos.ativo = 1
                ORDER BY pratos.nome
            """).fetchall()
            return pratos
        finally:
            conexao.close()

    @staticmethod
    def listar_todos():
        conexao = conectar()
        try:
            pratos = conexao.execute("""
                SELECT
                    pratos.*,
                    COALESCE(estoque_pratos.quantidade, 50) AS estoque
                FROM pratos
                LEFT JOIN estoque_pratos ON estoque_pratos.prato_id = pratos.id
                ORDER BY pratos.id DESC
            """).fetchall()
            return [dict(prato) for prato in pratos]
        finally:
            conexao.close()

    @staticmethod
    def buscar(id_prato):
        conexao = conectar()
        try:
            prato = conexao.execute("""
                SELECT
                    pratos.*,
                    COALESCE(estoque_pratos.quantidade, 50) AS estoque
                FROM pratos
                LEFT JOIN estoque_pratos ON estoque_pratos.prato_id = pratos.id
                WHERE pratos.id = ?
            """, (id_prato,)).fetchone()
            return prato
        finally:
            conexao.close()

    @staticmethod
    def cadastrar(nome, descricao, preco, categoria="Pratos", imagem=None, tempo_preparo_min=20, estoque=50):
        conexao = conectar()
        try:
            cursor = conexao.execute("""
                INSERT INTO pratos (nome, descricao, preco, categoria, imagem, tempo_preparo_min)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, descricao, preco, categoria, imagem, int(tempo_preparo_min or 20)))

            id_prato = cursor.lastrowid
            conexao.execute("""
                INSERT OR REPLACE INTO estoque_pratos (prato_id, quantidade)
                VALUES (?, ?)
            """, (id_prato, max(0, int(estoque if estoque is not None else 50))))

            conexao.commit()
            return id_prato
        finally:
            conexao.close()

    @staticmethod
    def atualizar(
        id_prato,
        nome,
        descricao,
        preco,
        ativo,
        categoria="Pratos",
        imagem=None,
        tempo_preparo_min=None,
        estoque=None,
        remover_imagem=False
    ):
        conexao = conectar()
        try:
            if remover_imagem:
                conexao.execute("""
                    UPDATE pratos
                    SET
                        nome = ?,
                        descricao = ?,
                        preco = ?,
                        ativo = ?,
                        categoria = ?,
                        imagem = NULL,
                        tempo_preparo_min = COALESCE(?, tempo_preparo_min)
                    WHERE id = ?
                """, (
                    nome,
                    descricao,
                    preco,
                    ativo,
                    categoria,
                    int(tempo_preparo_min) if tempo_preparo_min is not None else None,
                    id_prato
                ))
            else:
                conexao.execute("""
                    UPDATE pratos
                    SET
                        nome = ?,
                        descricao = ?,
                        preco = ?,
                        ativo = ?,
                        categoria = ?,
                        imagem = COALESCE(?, imagem),
                        tempo_preparo_min = COALESCE(?, tempo_preparo_min)
                    WHERE id = ?
                """, (
                    nome,
                    descricao,
                    preco,
                    ativo,
                    categoria,
                    imagem,
                    int(tempo_preparo_min) if tempo_preparo_min is not None else None,
                    id_prato
                ))

            if estoque is not None:
                conexao.execute("""
                    INSERT OR REPLACE INTO estoque_pratos (prato_id, quantidade)
                    VALUES (?, ?)
                """, (id_prato, max(0, int(estoque))))

            conexao.commit()
        finally:
            conexao.close()

    @staticmethod
    def atualizar_estoque(id_prato, quantidade):
        if isinstance(quantidade, bool) or quantidade is None:
            raise ValueError("Quantidade inválida.")
        qtd_int = int(quantidade)
        if qtd_int < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")
        conexao = conectar()
        try:
            conexao.execute("""
                INSERT OR REPLACE INTO estoque_pratos (prato_id, quantidade)
                VALUES (?, ?)
            """, (id_prato, qtd_int))
            conexao.commit()
        finally:
            conexao.close()

    @staticmethod
    def alertas_estoque(limite=10):
        conexao = conectar()
        try:
            linhas = conexao.execute("""
                SELECT
                    pratos.id,
                    pratos.nome,
                    pratos.categoria,
                    COALESCE(estoque_pratos.quantidade, 0) AS estoque,
                    CASE
                        WHEN COALESCE(estoque_pratos.quantidade, 0) = 0 THEN 'ESGOTADO'
                        WHEN COALESCE(estoque_pratos.quantidade, 0) <= ? THEN 'ESTOQUE BAIXO'
                        ELSE 'NORMAL'
                    END AS status_estoque
                FROM pratos
                LEFT JOIN estoque_pratos ON estoque_pratos.prato_id = pratos.id
                WHERE COALESCE(estoque_pratos.quantidade, 0) <= ?
                ORDER BY estoque ASC, pratos.nome ASC
            """, (limite, limite)).fetchall()
            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()

    @staticmethod
    def excluir(id_prato):
        conexao = conectar()
        try:
            conexao.execute("""
                UPDATE pratos SET ativo = 0 WHERE id = ?
            """, (id_prato,))

            conexao.commit()
        finally:
            conexao.close()
