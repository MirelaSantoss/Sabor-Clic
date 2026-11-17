from app.middleware import limpar_texto


class Endereco:

    def __init__(self, rua, numero, bairro, cidade, estado, cep):
        self.rua = limpar_texto(rua)
        self.numero = limpar_texto(numero)
        self.bairro = limpar_texto(bairro)
        self.cidade = limpar_texto(cidade)
        self.estado = limpar_texto(estado)
        self.cep = limpar_texto(cep)

    def valido(self):
        return all([
            self.rua,
            self.numero,
            self.bairro,
            self.cidade,
            self.estado,
            self.cep
        ])

    def dicionario(self):
        return {
            "rua": self.rua,
            "numero": self.numero,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado,
            "cep": self.cep
        }

    def tupla(self):
        return (
            self.rua,
            self.numero,
            self.bairro,
            self.cidade,
            self.estado,
            self.cep
        )
