# Sabor & Clic — projeto escolar

## Executar

1. Instale Python 3.11+ e execute `pip install -r requirements.txt`.
2. Execute `python run.py` e abra http://127.0.0.1:5000/.
3. Para criar uma conta de cozinheiro ou administrador, execute `python criar_funcionario.py` e escolha o tipo. Use a opção **Entrar como funcionário** na tela de login.
4. Clientes se cadastram pelo formulário e informam o endereço. O banco `sabor_clic.db` é criado automaticamente.

## Funcionalidades

- Cliente: cadastro em duas etapas, login, categorias do cardápio, busca, detalhes, carrinho e pedidos.
- Cozinheiro: três colunas de status e atualização automática a cada 15 segundos.
- Administrador: painel, inclusão de produto com foto, edição/desativação, resumo de vendas e lista de funcionários. Cadastro de funcionários via script local.
- SQLite com chave estrangeira, persistência de pedidos, senhas com hash, registro de mudança de status por trigger e rotas protegidas.

## Observações

Este é um projeto de demonstração local. O carrinho fica no armazenamento local do navegador; os pedidos e usuários ficam no SQLite. O preço final é calculado no servidor. Os scripts SQL antigos (MySQL) foram preservados como referência, mas a aplicação executa com SQLite. Não publique o servidor de desenvolvimento na internet. A integração de pagamentos reais, reserva de espaços, documentação de DER/dicionário de dados e testes de implantação não estão incluídos nesta versão. Revise os requisitos da disciplina antes da entrega.
