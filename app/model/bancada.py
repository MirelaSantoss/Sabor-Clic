import math
import sqlite3
from datetime import datetime
from app.db import conectar
from app.middleware import limpar_texto, converter_preco

STATUS_BANCADA_VALIDOS = ("DISPONIVEL", "MANUTENCAO", "INATIVA")
STATUS_RESERVA_VALIDOS = ("SOLICITADA", "CONFIRMADA", "CONCLUIDA", "CANCELADA")


def _converter_data_hora(valor):
    texto = limpar_texto(valor).replace("T", " ")
    for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(texto, formato)
            return dt, dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    raise ValueError("Formato de data e hora inválido. Use AAAA-MM-DD HH:MM.")


def _converter_caucao_ou_adicional(valor, nome_campo="Valor"):
    if isinstance(valor, bool) or valor is None:
        raise ValueError(f"{nome_campo} inválido.")
    texto = str(valor).strip().replace(",", ".")
    numero = float(texto)
    if math.isnan(numero) or math.isinf(numero) or numero < 0:
        raise ValueError(f"{nome_campo} não pode ser negativo.")
    return round(numero, 2)


class Bancada:

    @staticmethod
    def listar(apenas_disponiveis=False):
        conexao = conectar()
        try:
            if apenas_disponiveis:
                linhas = conexao.execute("""
                    SELECT *, id AS id_bancada FROM bancadas
                    WHERE status_operacional = 'DISPONIVEL'
                    ORDER BY cod_identificacao
                """).fetchall()
            else:
                linhas = conexao.execute("""
                    SELECT *, id AS id_bancada FROM bancadas
                    ORDER BY id
                """).fetchall()
            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()

    @staticmethod
    def buscar(id_bancada):
        conexao = conectar()
        try:
            linha = conexao.execute(
                "SELECT *, id AS id_bancada FROM bancadas WHERE id = ?",
                (id_bancada,)
            ).fetchone()
            return dict(linha) if linha else None
        finally:
            conexao.close()

    @staticmethod
    def cadastrar(cod_identificacao, descricao, valor_hora, valor_caucao, status_operacional="DISPONIVEL"):
        codigo = limpar_texto(cod_identificacao).upper()
        desc = limpar_texto(descricao)
        if not codigo or len(codigo) > 20:
            raise ValueError("Informe um código de identificação válido (até 20 caracteres).")
        if not desc:
            raise ValueError("Informe a descrição e os equipamentos da bancada.")

        preco_hora = converter_preco(valor_hora)
        caucao = _converter_caucao_ou_adicional(valor_caucao, "Valor de caução")
        status = limpar_texto(status_operacional).upper() or "DISPONIVEL"
        if status not in STATUS_BANCADA_VALIDOS:
            raise ValueError("Status operacional inválido.")

        conexao = conectar()
        try:
            cursor = conexao.execute("""
                INSERT INTO bancadas (cod_identificacao, descricao, valor_hora, valor_caucao, status_operacional)
                VALUES (?, ?, ?, ?, ?)
            """, (codigo, desc, preco_hora, caucao, status))
            conexao.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            conexao.rollback()
            raise ValueError("Já existe uma bancada com este código de identificação.")
        finally:
            conexao.close()

    @staticmethod
    def atualizar(id_bancada, valor_hora, valor_caucao, descricao=None, status_operacional=None, cod_identificacao=None):
        bancada = Bancada.buscar(id_bancada)
        if not bancada:
            return 0

        preco_hora = converter_preco(valor_hora)
        caucao = _converter_caucao_ou_adicional(
            valor_caucao if valor_caucao is not None else bancada["valor_caucao"],
            "Valor de caução"
        )

        codigo_final = limpar_texto(cod_identificacao).upper() if cod_identificacao else bancada["cod_identificacao"]
        if not codigo_final or len(codigo_final) > 20:
            raise ValueError("Código de identificação inválido.")

        desc_final = limpar_texto(descricao) if descricao is not None else bancada["descricao"]
        if not desc_final:
            raise ValueError("A descrição da bancada não pode ficar vazia.")

        status_final = limpar_texto(status_operacional).upper() if status_operacional else bancada["status_operacional"]
        if status_final not in STATUS_BANCADA_VALIDOS:
            raise ValueError("Status operacional inválido.")

        conexao = conectar()
        try:
            cursor = conexao.execute("""
                UPDATE bancadas
                SET cod_identificacao = ?, valor_hora = ?, valor_caucao = ?, descricao = ?, status_operacional = ?
                WHERE id = ?
            """, (codigo_final, preco_hora, caucao, desc_final, status_final, id_bancada))
            conexao.commit()
            return cursor.rowcount
        except sqlite3.IntegrityError:
            conexao.rollback()
            raise ValueError("Já existe outra bancada com este código de identificação.")
        finally:
            conexao.close()

    @staticmethod
    def criar_reserva(cliente_id, bancada_id, data_hora_inicio, data_hora_fim):
        if isinstance(bancada_id, bool) or bancada_id is None:
            raise ValueError("Bancada inválida.")
        id_bancada_int = int(bancada_id)

        dt_inicio, inicio_sql = _converter_data_hora(data_hora_inicio)
        dt_fim, fim_sql = _converter_data_hora(data_hora_fim)

        if dt_fim <= dt_inicio:
            raise ValueError("A data/hora final deve ser posterior à data/hora inicial.")

        horas = (dt_fim - dt_inicio).total_seconds() / 3600.0
        if horas < 1:
            raise ValueError("A reserva mínima é de 1 hora.")

        conexao = conectar()
        cursor = conexao.cursor()
        try:
            bancada = cursor.execute(
                "SELECT * FROM bancadas WHERE id = ?",
                (id_bancada_int,)
            ).fetchone()

            if bancada is None:
                raise ValueError("Bancada não encontrada.")

            if bancada["status_operacional"] != "DISPONIVEL":
                raise ValueError("Esta bancada não está disponível para locação.")

            conflito = cursor.execute("""
                SELECT id, data_hora_inicio, data_hora_fim FROM reservas_bancadas
                WHERE bancada_id = ?
                  AND status_reserva IN ('SOLICITADA', 'CONFIRMADA')
                  AND data_hora_inicio < ?
                  AND data_hora_fim > ?
            """, (id_bancada_int, fim_sql, inicio_sql)).fetchone()

            if conflito is not None:
                raise ValueError(
                    f"Conflito de horário: a bancada já está reservada de {conflito['data_hora_inicio']} até {conflito['data_hora_fim']}."
                )

            valor_total_horas = round(horas * float(bancada["valor_hora"]), 2)
            valor_caucao_pago = round(float(bancada["valor_caucao"]), 2)

            cursor.execute("""
                INSERT INTO reservas_bancadas
                (cliente_id, bancada_id, data_hora_inicio, data_hora_fim,
                 valor_total_horas, valor_caucao_pago, valor_adicionais, status_reserva)
                VALUES (?, ?, ?, ?, ?, ?, 0, 'CONFIRMADA')
            """, (
                cliente_id,
                id_bancada_int,
                inicio_sql,
                fim_sql,
                valor_total_horas,
                valor_caucao_pago
            ))

            conexao.commit()
            return {
                "id_reserva": cursor.lastrowid,
                "valor_total_horas": valor_total_horas,
                "valor_caucao_pago": valor_caucao_pago,
                "status_reserva": "CONFIRMADA"
            }
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()

    @staticmethod
    def buscar_reserva(id_reserva):
        conexao = conectar()
        try:
            linha = conexao.execute("""
                SELECT
                    r.*,
                    r.id AS id_reserva,
                    b.cod_identificacao,
                    b.descricao AS bancada_descricao
                FROM reservas_bancadas r
                JOIN bancadas b ON b.id = r.bancada_id
                WHERE r.id = ?
            """, (id_reserva,)).fetchone()
            return dict(linha) if linha else None
        finally:
            conexao.close()

    @staticmethod
    def atualizar_reserva_admin(
        id_reserva,
        bancada_id=None,
        data_hora_inicio=None,
        data_hora_fim=None,
        status_reserva=None,
        valor_adicionais=None
    ):
        reserva_atual = Bancada.buscar_reserva(id_reserva)
        if not reserva_atual:
            return 0

        id_bancada_final = int(bancada_id if bancada_id is not None else reserva_atual["bancada_id"])
        dt_inicio, inicio_sql = _converter_data_hora(
            data_hora_inicio if data_hora_inicio is not None else reserva_atual["data_hora_inicio"]
        )
        dt_fim, fim_sql = _converter_data_hora(
            data_hora_fim if data_hora_fim is not None else reserva_atual["data_hora_fim"]
        )

        if dt_fim <= dt_inicio:
            raise ValueError("A data/hora final deve ser posterior à data/hora inicial.")

        horas = (dt_fim - dt_inicio).total_seconds() / 3600.0
        if horas < 1:
            raise ValueError("A reserva mínima é de 1 hora.")

        status_final = limpar_texto(status_reserva or reserva_atual["status_reserva"]).upper()
        if status_final not in STATUS_RESERVA_VALIDOS:
            raise ValueError("Status de reserva inválido.")

        adicionais_final = _converter_caucao_ou_adicional(
            valor_adicionais if valor_adicionais is not None else reserva_atual["valor_adicionais"],
            "Valor de adicionais"
        )

        conexao = conectar()
        cursor = conexao.cursor()
        try:
            bancada = cursor.execute(
                "SELECT * FROM bancadas WHERE id = ?",
                (id_bancada_final,)
            ).fetchone()
            if bancada is None:
                raise ValueError("Bancada não encontrada.")

            if status_final in ("SOLICITADA", "CONFIRMADA"):
                conflito = cursor.execute("""
                    SELECT id, data_hora_inicio, data_hora_fim FROM reservas_bancadas
                    WHERE id <> ?
                      AND bancada_id = ?
                      AND status_reserva IN ('SOLICITADA', 'CONFIRMADA')
                      AND data_hora_inicio < ?
                      AND data_hora_fim > ?
                """, (id_reserva, id_bancada_final, fim_sql, inicio_sql)).fetchone()

                if conflito is not None:
                    raise ValueError(
                        f"Conflito de horário na bancada: já existe a reserva #{conflito['id']} de {conflito['data_hora_inicio']} até {conflito['data_hora_fim']}."
                    )

            valor_total_horas = round(horas * float(bancada["valor_hora"]), 2)
            valor_caucao_pago = round(float(bancada["valor_caucao"]), 2)

            cursor.execute("""
                UPDATE reservas_bancadas
                SET
                    bancada_id = ?,
                    data_hora_inicio = ?,
                    data_hora_fim = ?,
                    valor_total_horas = ?,
                    valor_caucao_pago = ?,
                    valor_adicionais = ?,
                    status_reserva = ?
                WHERE id = ?
            """, (
                id_bancada_final,
                inicio_sql,
                fim_sql,
                valor_total_horas,
                valor_caucao_pago,
                adicionais_final,
                status_final,
                id_reserva
            ))
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()

    @staticmethod
    def atualizar_reserva_cliente(
        id_reserva,
        cliente_id,
        bancada_id=None,
        data_hora_inicio=None,
        data_hora_fim=None,
        cancelar=False
    ):
        reserva_atual = Bancada.buscar_reserva(id_reserva)
        if not reserva_atual or int(reserva_atual["cliente_id"]) != int(cliente_id):
            raise PermissionError("Reserva não encontrada para este cliente.")

        if reserva_atual["status_reserva"] in ("CONCLUIDA", "CANCELADA"):
            raise ValueError("Não é possível alterar uma reserva já concluída ou cancelada.")

        if cancelar:
            conexao = conectar()
            try:
                conexao.execute(
                    "UPDATE reservas_bancadas SET status_reserva = 'CANCELADA' WHERE id = ? AND cliente_id = ?",
                    (id_reserva, cliente_id)
                )
                conexao.commit()
                return {"id_reserva": id_reserva, "status_reserva": "CANCELADA"}
            finally:
                conexao.close()

        Bancada.atualizar_reserva_admin(
            id_reserva,
            bancada_id=bancada_id,
            data_hora_inicio=data_hora_inicio,
            data_hora_fim=data_hora_fim,
            status_reserva=reserva_atual["status_reserva"],
            valor_adicionais=reserva_atual["valor_adicionais"]
        )
        return Bancada.buscar_reserva(id_reserva)

    @staticmethod
    def agenda_ocupacao(bancada_id=None, data_filtro=None, incluir_cliente=False):
        conexao = conectar()
        try:
            filtros = []
            parametros = []

            if not incluir_cliente:
                filtros.append("r.status_reserva IN ('SOLICITADA', 'CONFIRMADA')")

            if bancada_id:
                filtros.append("r.bancada_id = ?")
                parametros.append(int(bancada_id))

            if data_filtro:
                data_limpa = limpar_texto(data_filtro)[:10]
                if data_limpa:
                    filtros.append("(substr(r.data_hora_inicio, 1, 10) <= ? AND substr(r.data_hora_fim, 1, 10) >= ?)")
                    parametros.extend([data_limpa, data_limpa])

            clausula_where = ("WHERE " + " AND ".join(filtros)) if filtros else ""

            if incluir_cliente:
                consulta = f"""
                    SELECT
                        r.*,
                        r.id AS id_reserva,
                        ROUND((julianday(r.data_hora_fim) - julianday(r.data_hora_inicio)) * 24.0, 1) AS duracao_horas,
                        b.cod_identificacao,
                        b.descricao AS bancada_descricao,
                        b.valor_hora,
                        b.valor_caucao,
                        b.status_operacional,
                        c.nome AS cliente_nome,
                        c.email AS cliente_email,
                        c.telefone AS cliente_telefone
                    FROM reservas_bancadas r
                    JOIN bancadas b ON b.id = r.bancada_id
                    JOIN clientes c ON c.id = r.cliente_id
                    {clausula_where}
                    ORDER BY r.data_hora_inicio ASC, r.id ASC
                """
            else:
                consulta = f"""
                    SELECT
                        r.id AS id_reserva,
                        r.bancada_id,
                        r.data_hora_inicio,
                        r.data_hora_fim,
                        ROUND((julianday(r.data_hora_fim) - julianday(r.data_hora_inicio)) * 24.0, 1) AS duracao_horas,
                        r.status_reserva,
                        b.cod_identificacao,
                        b.descricao AS bancada_descricao,
                        b.valor_hora,
                        b.valor_caucao,
                        b.status_operacional
                    FROM reservas_bancadas r
                    JOIN bancadas b ON b.id = r.bancada_id
                    {clausula_where}
                    ORDER BY r.data_hora_inicio ASC, r.id ASC
                """

            linhas = conexao.execute(consulta, tuple(parametros)).fetchall()
            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()

    @staticmethod
    def listar_reservas(cliente_id=None):
        conexao = conectar()
        try:
            if cliente_id is not None:
                linhas = conexao.execute("""
                    SELECT
                        r.*,
                        r.id AS id_reserva,
                        ROUND((julianday(r.data_hora_fim) - julianday(r.data_hora_inicio)) * 24.0, 1) AS duracao_horas,
                        b.cod_identificacao,
                        b.descricao AS bancada_descricao,
                        b.valor_hora,
                        b.valor_caucao
                    FROM reservas_bancadas r
                    JOIN bancadas b ON b.id = r.bancada_id
                    WHERE r.cliente_id = ?
                    ORDER BY r.data_hora_inicio DESC
                """, (cliente_id,)).fetchall()
            else:
                linhas = conexao.execute("""
                    SELECT
                        r.*,
                        r.id AS id_reserva,
                        ROUND((julianday(r.data_hora_fim) - julianday(r.data_hora_inicio)) * 24.0, 1) AS duracao_horas,
                        b.cod_identificacao,
                        b.descricao AS bancada_descricao,
                        b.valor_hora,
                        b.valor_caucao,
                        c.nome AS cliente_nome,
                        c.email AS cliente_email,
                        c.telefone AS cliente_telefone
                    FROM reservas_bancadas r
                    JOIN bancadas b ON b.id = r.bancada_id
                    JOIN clientes c ON c.id = r.cliente_id
                    ORDER BY r.data_hora_inicio ASC
                """).fetchall()
            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()

    @staticmethod
    def produtividade():
        conexao = conectar()
        try:
            linhas = conexao.execute("""
                SELECT
                    b.id,
                    b.cod_identificacao,
                    b.descricao,
                    b.valor_hora,
                    b.valor_caucao,
                    b.status_operacional,
                    COUNT(r.id) AS total_locacoes,
                    ROUND(COALESCE(SUM((julianday(r.data_hora_fim) - julianday(r.data_hora_inicio)) * 24.0), 0), 1) AS total_horas_utilizadas,
                    ROUND(COALESCE(SUM(r.valor_total_horas + r.valor_adicionais), 0), 2) AS receita_total_gerada
                FROM bancadas b
                LEFT JOIN reservas_bancadas r
                    ON r.bancada_id = b.id
                    AND r.status_reserva IN ('CONFIRMADA', 'CONCLUIDA')
                GROUP BY b.id
                ORDER BY receita_total_gerada DESC, b.id ASC
            """).fetchall()
            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()
