from endereco import Endereco
class Cliente():
    
    def __init__(self, id, nome, telefone, cpf, data_nascimento, email, senha, genero, endereco):
        self.id = id
        self.nome = nome 
        self.telefone = telefone
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.email = email
        self.senha = senha
        self.genero = genero
        self.endereco = endereco