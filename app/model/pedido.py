class Pedido:
    proximo_id = 1

    def __init__(self, cliente, endereco, itens):

        self.id = Pedido.proximo_id 
        Pedido.proximo_id +=1

        self.cliente = cliente
        self.endereco = endereco
        self.itens = itens 
        self.status = "Aguardando"

        self.subtotal = self.calcular_subtotal()
        self.total = self.calcular_total()

    def calcular_subtotal(self):
        subtotal = 0

        for prato in self.itens:
            subtotal += prato.preco

        return subtotal

    def iniciar_preparo(self):
        self.status = "Iniciando Preparo"


    def pedido_dicionario(self):
        return {
            "cliente": self.cliente,
            "endereco": self.endereco.rua,
            "itens": [{"nome": prato.nome, "pedido": prato.preco }
                      for prato in self.itens],
            "subtotal": self.subtotal,
            "total": self.total,
            "status": self.status

        }
