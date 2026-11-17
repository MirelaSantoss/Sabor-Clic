# Sabor & Clic — Sistema de Gestão para Dark Kitchens e Espaços Gastronômicos

## Executar

1. Instale Python 3.11+ e execute `pip install -r requirements.txt`.
2. Execute `python run.py` e abra `http://127.0.0.1:5000/`.
3. Para criar uma conta de cozinheiro ou administrador via terminal, execute `python criar_funcionario.py` e informe os dados solicitados.
4. Clientes se cadastram pelo formulário em duas etapas (`/formulario` e `/endereco`). O banco `sabor_clic.db` é criado e migrado automaticamente.

## Funcionalidades

- **Cliente:** cadastro em duas etapas com validação de dados, login com sessão temporizada, cardápio digital por categorias e busca, detalhes do produto com observações, carrinho orientando a objetos, histórico de pedidos e agendamento de bancadas gastronômicas com verificação de conflito de horário.
- **Cozinheiro (KDS):** painel em tempo real com contador de pedidos pendentes, três colunas de status, suporte a arrastar e soltar (drag-and-drop), definição de tempo estimado de preparo, destaque de observações e atualização automática a cada 15 segundos.
- **Administrador:** painel de gestão de pratos (cadastro com upload de imagem, edição de preço/categoria e ativação/desativação), gestão de bancadas (preço por hora, caução e status operacional), resumo de vendas e cadastro de funcionários.
- **Banco de Dados e Segurança:** SQLite com chaves estrangeiras e triggers ativas (`registrar_status`, `conferir_estoque_antes_pedido`, `baixar_estoque_pedido`), scripts MySQL completos na pasta `sql/` (`01_modelo_fisico.sql`, `02_insercoes_basicas.sql`, `11_queries_relatorios.sql`, `20_triggers.sql`), RBAC por middleware, senhas com hash criptográfico, sanitização contra HTML/SQL Injection e cookies `HttpOnly`.
