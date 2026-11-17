import sys
from app.db import conectar, criar_tabelas, DB_PATH


def limpar_banco():
    criar_tabelas()
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.executescript("""
        DELETE FROM historico_status;
        DELETE FROM pedido_itens;
        DELETE FROM pedidos;
        DELETE FROM reservas_bancadas;
        DELETE FROM cadastros_pendentes;
        DELETE FROM clientes;
        DELETE FROM enderecos;
        DELETE FROM estoque_pratos;
        DELETE FROM pratos;
        DELETE FROM bancadas;
        DELETE FROM sqlite_sequence;
    """)
    conexao.commit()
    conexao.close()
    criar_tabelas()
    print("Banco de dados limpo e restaurado com os pratos e bancadas padrão!")


def verificar_banco():
    criar_tabelas()
    print(f"Banco consultado: {DB_PATH}")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("DROP TABLE IF EXISTS Usuario")
    conexao.commit()

    for perfil, titulo in (
        ("administrador", "Administradores"),
        ("cozinheiro", "Cozinheiros"),
        ("cliente", "Clientes")
    ):
        lista = cursor.execute(
            "SELECT id, nome, email, telefone, cpf FROM clientes WHERE tipo = ? ORDER BY id",
            (perfil,)
        ).fetchall()
        print(f"\n=== {titulo} ({len(lista)}) ===")
        if not lista:
            print("  Nenhum cadastrado.")
        for u in lista:
            extras = f" | Tel: {u['telefone'] or '-'} | CPF: {u['cpf'] or '-'}" if perfil == "cliente" else ""
            print(f"  ID: {u['id']} | Nome: {u['nome']} | E-mail: {u['email']}{extras}")

    pratos = cursor.execute(
        "SELECT id, nome, categoria, preco, ativo FROM pratos ORDER BY id"
    ).fetchall()
    print(f"\n=== Pratos ({len(pratos)}) ===")
    for p in pratos:
        status = "Ativo" if p["ativo"] else "Inativo"
        print(f"  ID: {p['id']} | {p['nome']} ({p['categoria']}) | R$ {p['preco']:.2f} | {status}")

    bancadas = cursor.execute(
        "SELECT id, cod_identificacao, valor_hora, valor_caucao, status_operacional FROM bancadas ORDER BY id"
    ).fetchall()
    print(f"\n=== Bancadas ({len(bancadas)}) ===")
    for b in bancadas:
        print(
            f"  ID: {b['id']} | {b['cod_identificacao']} | "
            f"Hora: R$ {b['valor_hora']:.2f} | Caução: R$ {b['valor_caucao']:.2f} | {b['status_operacional']}"
        )

    total_pedidos = cursor.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    total_reservas = cursor.execute("SELECT COUNT(*) FROM reservas_bancadas").fetchone()[0]
    print(f"\nTotal de pedidos registrados: {total_pedidos}")
    print(f"Total de reservas de bancadas: {total_reservas}")

    conexao.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("limpar", "--limpar", "reset", "--reset"):
        limpar_banco()
    verificar_banco()
