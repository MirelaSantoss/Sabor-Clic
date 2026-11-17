import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

from app.db import conectar
from app.model.endereco import Endereco
from app.middleware import limpar_texto, email_valido, senha_valida


class Cliente:

    PERFIS_VALIDOS = ("cliente", "cozinheiro", "administrador")

    @staticmethod
    def criar_cadastro_pendente(dados):
        nome = limpar_texto(dados.get("nome"))
        telefone = limpar_texto(dados.get("telefone"))
        cpf = limpar_texto(dados.get("cpf"))
        data_nascimento = limpar_texto(dados.get("data_nascimento"))
        email = limpar_texto(dados.get("email")).lower()
        senha = dados.get("senha") or ""
        genero = limpar_texto(dados.get("genero")) or None

        if not all([nome, telefone, cpf, data_nascimento, email, senha]):
            raise ValueError("Preencha todos os campos obrigatórios.")

        if not email_valido(email):
            raise ValueError("Informe um e-mail válido com no máximo 120 caracteres.")

        if not senha_valida(senha):
            raise ValueError("A senha deve ter pelo menos 8 caracteres, misturando letras e números.")

        conexao = conectar()

        try:
            existente = conexao.execute(
                "SELECT id FROM clientes WHERE email = ? OR cpf = ?",
                (email, cpf)
            ).fetchone()

            if existente is not None:
                raise sqlite3.IntegrityError("CPF ou e-mail já cadastrado.")

            conexao.execute(
                "DELETE FROM cadastros_pendentes WHERE email = ? OR cpf = ?",
                (email, cpf)
            )

            senha_hash = generate_password_hash(senha)

            cursor = conexao.execute("""
                INSERT INTO cadastros_pendentes
                (nome, telefone, cpf, data_nascimento, email, senha_hash, genero)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                nome,
                telefone,
                cpf,
                data_nascimento,
                email,
                senha_hash,
                genero
            ))

            conexao.commit()
            return cursor.lastrowid

        except Exception:
            conexao.rollback()
            raise

        finally:
            conexao.close()

    @staticmethod
    def cadastrar(pending_id, dados_endereco):
        obj_endereco = (
            dados_endereco
            if isinstance(dados_endereco, Endereco)
            else Endereco(
                dados_endereco.get("rua"),
                dados_endereco.get("numero"),
                dados_endereco.get("bairro"),
                dados_endereco.get("cidade"),
                dados_endereco.get("estado"),
                dados_endereco.get("cep")
            )
        )

        if not obj_endereco.valido():
            raise ValueError("Preencha todos os campos do endereço.")

        conexao = conectar()

        try:
            pendente = conexao.execute(
                "SELECT * FROM cadastros_pendentes WHERE id = ?",
                (pending_id,)
            ).fetchone()

            if pendente is None:
                raise ValueError("Cadastro temporário não encontrado.")

            cursor = conexao.execute("""
                INSERT INTO enderecos
                (rua, numero, bairro, cidade, estado, cep)
                VALUES (?, ?, ?, ?, ?, ?)
            """, obj_endereco.tupla())

            endereco_id = cursor.lastrowid

            cursor = conexao.execute("""
                INSERT INTO clientes
                (nome, telefone, cpf, data_nascimento, email, senha, genero, tipo, endereco_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'cliente', ?)
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

            conexao.execute(
                "DELETE FROM cadastros_pendentes WHERE id = ?",
                (pending_id,)
            )

            conexao.commit()
            return cursor.lastrowid

        except Exception:
            conexao.rollback()
            raise

        finally:
            conexao.close()

    @staticmethod
    def cadastrar_funcionario(nome, email, senha, tipo, telefone=None):
        if tipo not in ("cozinheiro", "administrador"):
            raise ValueError("Tipo de funcionário inválido.")

        nome_limpo = limpar_texto(nome)
        email_limpo = limpar_texto(email).lower()
        telefone_limpo = limpar_texto(telefone) or None

        if not nome_limpo or not email_valido(email_limpo) or not senha_valida(senha or ""):
            raise ValueError(
                "Informe nome, e-mail válido (até 120 caracteres) e senha com pelo menos 8 caracteres misturando letras e números."
            )

        conexao = conectar()

        try:
            existente = conexao.execute(
                "SELECT id FROM clientes WHERE email = ?",
                (email_limpo,)
            ).fetchone()

            if existente:
                raise ValueError("Este e-mail já está cadastrado.")

            senha_hash = generate_password_hash(senha)

            cursor = conexao.execute("""
                INSERT INTO clientes
                (nome, telefone, cpf, data_nascimento, email, senha, tipo)
                VALUES (?, ?, NULL, NULL, ?, ?, ?)
            """, (nome_limpo, telefone_limpo, email_limpo, senha_hash, tipo))

            conexao.commit()
            return cursor.lastrowid

        except Exception:
            conexao.rollback()
            raise

        finally:
            conexao.close()

    @staticmethod
    def listar_funcionarios():
        conexao = conectar()
        try:
            linhas = conexao.execute("""
                SELECT id, nome, email, tipo, telefone
                FROM clientes
                WHERE tipo IN ('administrador', 'cozinheiro')
                ORDER BY id
            """).fetchall()
            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()

    @staticmethod
    def autenticar(email, senha):
        email_normalizado = (email or "").strip().lower()
        if not email_normalizado or not senha:
            return None

        conexao = conectar()

        try:
            usuario = conexao.execute("""
                SELECT id, nome, email, senha, tipo
                FROM clientes
                WHERE email = ?
            """, (email_normalizado,)).fetchone()

            if usuario and check_password_hash(usuario["senha"], senha):
                return {
                    "id": usuario["id"],
                    "nome": usuario["nome"],
                    "email": usuario["email"],
                    "tipo": usuario["tipo"]
                }

            return None

        finally:
            conexao.close()

    @staticmethod
    def buscar_por_id(id_cliente):
        conexao = conectar()

        try:
            usuario = conexao.execute("""
                SELECT id, nome, email, tipo
                FROM clientes
                WHERE id = ?
            """, (id_cliente,)).fetchone()

            return dict(usuario) if usuario else None

        finally:
            conexao.close()
