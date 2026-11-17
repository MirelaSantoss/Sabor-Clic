from app.db import conectar


class Prato:

    @staticmethod
    def listar():
        conexao = conectar()
        try:
            pratos = conexao.execute("""
                SELECT * FROM pratos
                WHERE ativo = 1
                ORDER BY nome
            """).fetchall()
            return pratos
        finally:
            conexao.close()

    @staticmethod
    def listar_todos():
        conexao = conectar()
        try:
            pratos = conexao.execute("""
                SELECT * FROM pratos
                ORDER BY id DESC
            """).fetchall()
            return [dict(prato) for prato in pratos]
        finally:
            conexao.close()

    @staticmethod
    def buscar(id_prato):
        conexao = conectar()
        try:
            prato = conexao.execute("""
                SELECT * FROM pratos WHERE id = ?
            """, (id_prato,)).fetchone()
            return prato
        finally:
            conexao.close()

    @staticmethod
    def cadastrar(nome, descricao, preco, categoria="Pratos", imagem=None, tempo_preparo_min=20):
        conexao = conectar()
        try:
            cursor = conexao.execute("""
                INSERT INTO pratos (nome, descricao, preco, categoria, imagem, tempo_preparo_min)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, descricao, preco, categoria, imagem, int(tempo_preparo_min or 20)))

            conexao.commit()
            return cursor.lastrowid
        finally:
            conexao.close()

    @staticmethod
    def atualizar(id_prato, nome, descricao, preco, ativo, categoria="Pratos", imagem=None):
        conexao = conectar()
        try:
            conexao.execute("""
                UPDATE pratos
                SET nome = ?, descricao = ?, preco = ?, ativo = ?, categoria = ?, imagem = COALESCE(?, imagem)
                WHERE id = ?
            """, (nome, descricao, preco, ativo, categoria, imagem, id_prato))

            conexao.commit()
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
