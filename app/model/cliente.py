from werkzeug.security import generate_password_hash, check_password_hash

from app.db import conectar


class Cliente:

    @staticmethod
    def criar_cadastro_pendente(dados):
        """Salva temporariamente os dados do cadastro no banco."""

        conexao = conectar()

        try:
            senha_hash = generate_password_hash(dados["senha"])

            cursor = conexao.execute("""
                INSERT INTO cadastros_pendentes
                (nome, telefone, cpf, data_nascimento,
                 email, senha_hash, genero)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["nome"],
                dados["telefone"],
                dados["cpf"],
                dados["data_nascimento"],
                dados["email"],
                senha_hash,
                dados.get("genero")
            ))

            conexao.commit()

            return cursor.lastrowid

        except Exception:
            conexao.rollback()
            raise

        finally:
            conexao.close()

    @staticmethod
    def cadastrar(pending_id, endereco):
        """Finaliza o cadastro usando os dados temporários do banco."""

        conexao = conectar()

        try:
            pendente = conexao.execute("""
                SELECT * FROM cadastros_pendentes
                WHERE id = ?
            """, (pending_id,)).fetchone()

            if pendente is None:
                raise ValueError("Cadastro temporário não encontrado.")

            cursor = conexao.execute("""
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

            cursor = conexao.execute("""
                INSERT INTO clientes
                (nome, telefone, cpf, data_nascimento,
                 email, senha, genero, endereco_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pendente["nome"],
                pendente["telefone"],
                pendente["cpf"],
                pendente["data_nascimento"],
                pendente["email"],
                pendente["senha_hash"],
                pendente["genero"],
                endereco_id
            ))

            conexao.execute("""
                DELETE FROM cadastros_pendentes
                WHERE id = ?
            """, (pending_id,))

            conexao.commit()

            return cursor.lastrowid

        except Exception:
            conexao.rollback()
            raise

        finally:
            conexao.close()

    @staticmethod
    def autenticar(email, senha):
        """Verifica o e-mail e a senha do usuário."""

        conexao = conectar()

        try:
            usuario = conexao.execute("""
                SELECT * FROM clientes WHERE email = ?
            """, (email,)).fetchone()

            if usuario and check_password_hash(usuario["senha"], senha):
                return usuario

            return None

        finally:
            conexao.close()

    @staticmethod
    def buscar_por_id(id_cliente):
        """Busca os dados de um cliente pelo ID."""

        conexao = conectar()

        try:
            usuario = conexao.execute("""
                SELECT id, nome, email, tipo
                FROM clientes
                WHERE id = ?
            """, (id_cliente,)).fetchone()

            return usuario

        finally:
            conexao.close()
