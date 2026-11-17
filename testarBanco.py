from app.db import conectar, criar_tabelas, DB_PATH


def verificar_banco():
    criar_tabelas()
    print(f"Banco consultado: {DB_PATH}")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("DROP TABLE IF EXISTS Usuario")
    conexao.commit()

    tabelas = [
        r["name"]
        for r in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]
    triggers = [
        r["name"]
        for r in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type = 'trigger' ORDER BY name"
        ).fetchall()
    ]

    print(f"\nTabelas ativas ({len(tabelas)}): {', '.join(tabelas)}")
    print(f"Triggers ativas ({len(triggers)}): {', '.join(triggers)}")

    usuarios = cursor.execute(
        "SELECT id, nome, email, tipo FROM clientes ORDER BY id"
    ).fetchall()
    print(f"\nUsuários cadastrados ({len(usuarios)}):")
    for u in usuarios:
        print(f"  ID: {u['id']} | Nome: {u['nome']} | E-mail: {u['email']} | Perfil: {u['tipo']}")

    pratos = cursor.execute(
        "SELECT id, nome, categoria, preco, ativo FROM pratos ORDER BY id"
    ).fetchall()
    print(f"\nPratos cadastrados ({len(pratos)}):")
    for p in pratos:
        status = "Ativo" if p["ativo"] else "Inativo"
        print(f"  ID: {p['id']} | {p['nome']} ({p['categoria']}) | R$ {p['preco']:.2f} | {status}")

    bancadas = cursor.execute(
        "SELECT id, cod_identificacao, valor_hora, valor_caucao, status_operacional FROM bancadas ORDER BY id"
    ).fetchall()
    print(f"\nBancadas cadastradas ({len(bancadas)}):")
    for b in bancadas:
        print(
            f"  ID: {b['id']} | {b['cod_identificacao']} | "
            f"Hora: R$ {b['valor_hora']:.2f} | Caução: R$ {b['valor_caucao']:.2f} | {b['status_operacional']}"
        )

    conexao.close()


if __name__ == "__main__":
    verificar_banco()
