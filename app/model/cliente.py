from werkzeug.security import generate_password_hash, check_password_hash

from app.db import conectar


class Cliente:

    PERFIS_VALIDOS = ("cliente", "cozinheiro", "administrador")

    @staticmethod
    def criar_cadastro_pendente(dados):
        conexao = conectar()

        try:
            email = dados["email"].strip().lower()
            senha_hash = generate_password_hash(dados["senha"])

            cursor = conexao.execute("""
                INSERT INTO cadastros_pendentes
                (nome, telefone, cpf, data_nascimento,
                 email, senha_hash, genero)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["nome"].strip(),
                dados["telefone"].strip(),
                dados["cpf"].strip(),
                dados["data_nascimento"],
                email,
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
                 email, senha, genero, tipo, endereco_id)
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
    def cadastrar_funcionario(nome, email, senha, tipo, telefone=None):
        if tipo not in ("cozinheiro", "administrador"):
            raise ValueError("Tipo de funcionário inválido.")

        nome = (nome or "").strip()
        email = (email or "").strip().lower()
        telefone = (telefone or "").strip() or None

        if not nome or "@" not in email or len(senha or "") < 8:
            raise ValueError("Informe nome, e-mail válido e senha com pelo menos 8 caracteres.")

        conexao = conectar()

        try:
            existente = conexao.execute(
                "SELECT id FROM clientes WHERE email = ?",
                (email,)
            ).fetchone()

            if existente:
                raise ValueError("Este e-mail já está cadastrado.")

            senha_hash = generate_password_hash(senha)

            cursor = conexao.execute("""
                INSERT INTO clientes
                (nome, telefone, cpf, data_nascimento, email, senha, tipo)
                VALUES (?, ?, NULL, NULL, ?, ?, ?)
            """, (nome, telefone, email, senha_hash, tipo))

            conexao.commit()
            return cursor.lastrowid

        except Exception:
            conexao.rollback()
            raise

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