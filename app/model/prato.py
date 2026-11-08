from app.db import conectar


class Prato:

    @staticmethod
    def listar():

        conexao = conectar()

        pratos = conexao.execute("""
            SELECT * FROM pratos
            WHERE ativo = 1
            ORDER BY nome
        """).fetchall()

        conexao.close()

        return pratos

    @staticmethod
    def buscar(id_prato):

        conexao = conectar()

        prato = conexao.execute("""
            SELECT * FROM pratos WHERE id = ?
        """, (id_prato,)).fetchone()

        conexao.close()

        return prato

    @staticmethod
    def cadastrar(nome, descricao, preco):

        conexao = conectar()

        cursor = conexao.execute("""
            INSERT INTO pratos (nome, descricao, preco)
            VALUES (?, ?, ?)
        """, (nome, descricao, preco))

        conexao.commit()
        id_prato = cursor.lastrowid
        conexao.close()

        return id_prato

    @staticmethod
    def atualizar(id_prato, nome, descricao, preco, ativo):

        conexao = conectar()

        conexao.execute("""
            UPDATE pratos
            SET nome = ?, descricao = ?, preco = ?, ativo = ?
            WHERE id = ?
        """, (nome, descricao, preco, ativo, id_prato))

        conexao.commit()
        conexao.close()

    @staticmethod
    def excluir(id_prato):

        conexao = conectar()

        conexao.execute("""
            UPDATE pratos SET ativo = 0 WHERE id = ?
        """, (id_prato,))

        conexao.commit()
        conexao.close()