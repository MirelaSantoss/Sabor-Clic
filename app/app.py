from flask import Flask, jsonify
from controllers.prato_controller import cardapio, buscar_prato

app = Flask(__name__)

@app.route("/pratos", methods=["GET"])
def listar_pratos():
    return jsonify(cardapio())

@app.route("/pratos/<int:id>", methods = ["GET"])
def consultar_prato(id):
    prato = buscar_prato(id)

    if prato:
        return jsonify(prato)

    return jsonify({"erro": "Prato não encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=True)
