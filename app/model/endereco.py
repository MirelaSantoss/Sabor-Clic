class Endereco:

    def __init__(self, rua, numero, bairro, cidade, estado, cep):

        self.rua = rua
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep

    def dicionario(self):

        return {
            "rua": self.rua,
            "numero": self.numero,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado,
            "cep": self.cep
        }