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
    def atualizar_funcionario(id_funcionario, nome, email, tipo, telefone=None, nova_senha=None):
        if tipo not in ("cozinheiro", "administrador"):
            raise ValueError("Tipo de funcionário inválido.")

        nome_limpo = limpar_texto(nome)
        email_limpo = limpar_texto(email).lower()
        telefone_limpo = limpar_texto(telefone) or None

        if not nome_limpo or not email_valido(email_limpo):
            raise ValueError("Informe nome e e-mail válido (até 120 caracteres).")

        if nova_senha and not senha_valida(nova_senha):
            raise ValueError("A nova senha deve ter pelo menos 8 caracteres, misturando letras e números.")

        conexao = conectar()
        try:
            atual = conexao.execute(
                "SELECT * FROM clientes WHERE id = ? AND tipo IN ('cozinheiro', 'administrador')",
                (id_funcionario,)
            ).fetchone()
            if atual is None:
                return 0

            duplicado = conexao.execute(
                "SELECT id FROM clientes WHERE email = ? AND id <> ?",
                (email_limpo, id_funcionario)
            ).fetchone()
            if duplicado:
                raise ValueError("Este e-mail já está em uso por outro usuário.")

            if nova_senha:
                senha_hash = generate_password_hash(nova_senha)
                conexao.execute("""
                    UPDATE clientes
                    SET nome = ?, email = ?, telefone = ?, tipo = ?, senha = ?
                    WHERE id = ?
                """, (nome_limpo, email_limpo, telefone_limpo, tipo, senha_hash, id_funcionario))
            else:
                conexao.execute("""
                    UPDATE clientes
                    SET nome = ?, email = ?, telefone = ?, tipo = ?
                    WHERE id = ?
                """, (nome_limpo, email_limpo, telefone_limpo, tipo, id_funcionario))

            conexao.commit()
            return 1
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()

    @staticmethod
    def remover_funcionario(id_funcionario, id_admin_logado=None):
        if id_admin_logado is not None and int(id_funcionario) == int(id_admin_logado):
            raise ValueError("Você não pode excluir sua própria conta de administrador logada.")

        conexao = conectar()
        try:
            alvo = conexao.execute(
                "SELECT id, tipo FROM clientes WHERE id = ? AND tipo IN ('cozinheiro', 'administrador')",
                (id_funcionario,)
            ).fetchone()
            if alvo is None:
                return 0

            conexao.execute("DELETE FROM clientes WHERE id = ?", (id_funcionario,))
            conexao.commit()
            return 1
        except sqlite3.IntegrityError:
            conexao.rollback()
            raise ValueError("Não é possível remover este funcionário pois há registros vinculados.")
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
    def listar_clientes():
        conexao = conectar()
        try:
            linhas = conexao.execute("""
                SELECT
                    c.id,
                    c.nome,
                    c.email,
                    c.telefone,
                    c.cpf,
                    c.data_nascimento,
                    c.genero,
                    c.endereco_id,
                    e.rua,
                    e.numero,
                    e.bairro,
                    e.cidade,
                    e.estado,
                    e.cep
                FROM clientes c
                LEFT JOIN enderecos e ON e.id = c.endereco_id
                WHERE c.tipo = 'cliente'
                ORDER BY c.id DESC
            """).fetchall()
            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()

    @staticmethod
    def atualizar_cliente_admin(id_cliente, dados):
        nome = limpar_texto(dados.get("nome"))
        email = limpar_texto(dados.get("email")).lower()
        telefone = limpar_texto(dados.get("telefone")) or None
        cpf = limpar_texto(dados.get("cpf")) or None

        if not nome or not email_valido(email):
            raise ValueError("Informe nome e e-mail válido (até 120 caracteres).")

        conexao = conectar()
        try:
            cliente_atual = conexao.execute(
                "SELECT * FROM clientes WHERE id = ? AND tipo = 'cliente'",
                (id_cliente,)
            ).fetchone()
            if cliente_atual is None:
                return 0

            duplicado = conexao.execute(
                "SELECT id FROM clientes WHERE (email = ? OR (cpf IS NOT NULL AND cpf = ?)) AND id <> ?",
                (email, cpf, id_cliente)
            ).fetchone()
            if duplicado:
                raise ValueError("E-mail ou CPF já pertence a outro usuário.")

            conexao.execute("""
                UPDATE clientes
                SET nome = ?, email = ?, telefone = ?, cpf = ?
                WHERE id = ?
            """, (nome, email, telefone, cpf, id_cliente))

            rua = limpar_texto(dados.get("rua"))
            numero = limpar_texto(dados.get("numero"))
            bairro = limpar_texto(dados.get("bairro"))
            cidade = limpar_texto(dados.get("cidade"))
            estado = limpar_texto(dados.get("estado"))
            cep = limpar_texto(dados.get("cep"))

            if all([rua, numero, bairro, cidade, estado, cep]):
                if cliente_atual["endereco_id"]:
                    conexao.execute("""
                        UPDATE enderecos
                        SET rua = ?, numero = ?, bairro = ?, cidade = ?, estado = ?, cep = ?
                        WHERE id = ?
                    """, (rua, numero, bairro, cidade, estado, cep, cliente_atual["endereco_id"]))
                else:
                    cur = conexao.execute("""
                        INSERT INTO enderecos (rua, numero, bairro, cidade, estado, cep)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (rua, numero, bairro, cidade, estado, cep))
                    conexao.execute(
                        "UPDATE clientes SET endereco_id = ? WHERE id = ?",
                        (cur.lastrowid, id_cliente)
                    )

            conexao.commit()
            return 1
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
