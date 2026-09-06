class Prato:
    def __init__(self,id, nome, descricao, preco, ativo=True):
        self.id = id
        self.nome = nome 
        self.descricao = descricao
        self.preco = preco
        self.ativo = ativo

    def dicionario_js(self):
        return{
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "ativo": self.ativo
        }