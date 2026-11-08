from werkzeug.security import generate_password_hash, check_password_hash

from app.db import conectar


class Cliente:

    @staticmethod
    def cadastrar(dados, endereco):

        conexao = conectar()
        cursor = conexao.cursor()

        try:

            cursor.execute("""
                INSERT INTO enderecos
                (rua, numero, bairro, cidade, estado, cep)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                endereco["rua"],
                endereco["numero"],
                endereco["bairro"],
                endereco["cidade"],
                endereco["estado"],
                endereco["cep"]
            ))

            endereco_id = cursor.lastrowid

            senha_hash = generate_password_hash(dados["senha"])

            cursor.execute("""
                INSERT INTO clientes
                (nome, telefone, cpf, data_nascimento,
                 email, senha, genero, endereco_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["nome"],
                dados["telefone"],
                dados["cpf"],
                dados["data_nascimento"],
                dados["email"],
                senha_hash,
                dados.get("genero"),
                endereco_id
            ))

            conexao.commit()

            return cursor.lastrowid

        except Exception:
            conexao.rollback()
            raise

        finally:
            conexao.close()

    @staticmethod
    def autenticar(email, senha):

        conexao = conectar()

        usuario = conexao.execute("""
            SELECT * FROM clientes WHERE email = ?
        """, (email,)).fetchone()

        conexao.close()

        if usuario and check_password_hash(usuario["senha"], senha):
            return usuario

        return None

    @staticmethod
    def buscar_por_id(id_cliente):

        conexao = conectar()

        usuario = conexao.execute("""
            SELECT id, nome, email, tipo
            FROM clientes
            WHERE id = ?
        """, (id_cliente,)).fetchone()

        conexao.close()

        return usuario