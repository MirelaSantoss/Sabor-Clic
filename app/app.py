from flask import Flask, jsonify
from controllers.prato_controller import configurar_rotas

app = Flask(__name__, template_folder="views")

configurar_rotas(app)

if __name__ == '__main__':
    app.run(debug=True)


