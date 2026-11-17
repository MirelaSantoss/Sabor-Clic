import math
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
    def atualizar(id_bancada, valor_hora, valor_caucao, descricao=None, status_operacional=None):
        bancada = Bancada.buscar(id_bancada)
        if not bancada:
            return 0

        preco_hora = converter_preco(valor_hora)
        if isinstance(valor_caucao, bool):
            raise ValueError("Valor de caução inválido.")
        texto_caucao = str(valor_caucao if valor_caucao is not None else bancada["valor_caucao"]).strip().replace(",", ".")
        caucao = float(texto_caucao)
        if math.isnan(caucao) or math.isinf(caucao) or caucao < 0:
            raise ValueError("O valor de caução não pode ser negativo.")

        desc_final = limpar_texto(descricao) if descricao is not None else bancada["descricao"]
        status_final = limpar_texto(status_operacional).upper() if status_operacional else bancada["status_operacional"]
        if status_final not in STATUS_BANCADA_VALIDOS:
            raise ValueError("Status operacional inválido.")

        conexao = conectar()
        try:
            cursor = conexao.execute("""
                UPDATE bancadas
                SET valor_hora = ?, valor_caucao = ?, descricao = ?, status_operacional = ?
                WHERE id = ?
            """, (preco_hora, round(caucao, 2), desc_final, status_final, id_bancada))
            conexao.commit()
            return cursor.rowcount
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
                SELECT id FROM reservas_bancadas
                WHERE bancada_id = ?
                  AND status_reserva IN ('SOLICITADA', 'CONFIRMADA')
                  AND data_hora_inicio < ?
                  AND data_hora_fim > ?
            """, (id_bancada_int, fim_sql, inicio_sql)).fetchone()

            if conflito is not None:
                raise ValueError("Conflito de horário: a bancada já está reservada neste período.")

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
    def listar_reservas(cliente_id=None):
        conexao = conectar()
        try:
            if cliente_id is not None:
                linhas = conexao.execute("""
                    SELECT
                        r.*,
                        r.id AS id_reserva,
                        b.cod_identificacao,
                        b.descricao AS bancada_descricao
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
                        b.cod_identificacao,
                        b.descricao AS bancada_descricao,
                        c.nome AS cliente_nome
                    FROM reservas_bancadas r
                    JOIN bancadas b ON b.id = r.bancada_id
                    JOIN clientes c ON c.id = r.cliente_id
                    ORDER BY r.data_hora_inicio DESC
                """).fetchall()
            return [dict(linha) for linha in linhas]
        finally:
            conexao.close()
