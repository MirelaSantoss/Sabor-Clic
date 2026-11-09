USE sabor_e_clic;

INSERT INTO Usuario (id_usuario, nome, email, senha_hash, tipo_perfil, telefone) VALUES
(1, 'Gustavo Vieira Stoppa', 'gustavo.stoppa@saboreclic.com.br', '$2b$12$e8Y6V.oHq.oQ5u2oJ9C6vOGZ4H7Q4l5O0V1B3J4K5L6M7N8O9P0Q1', 'GERENTE', '(11) 98765-4321'),
(2, 'Luis Fernando Lima de Clares', 'luis.clares@saboreclic.com.br', '$2b$12$e8Y6V.oHq.oQ5u2oJ9C6vOGZ4H7Q4l5O0V1B3J4K5L6M7N8O9P0Q2', 'OPERADOR', '(11) 97654-3210'),
(3, 'Mirela de Fatima Fernandes dos Santos', 'mirela.santos@deliverygourmet.com', '$2b$12$e8Y6V.oHq.oQ5u2oJ9C6vOGZ4H7Q4l5O0V1B3J4K5L6M7N8O9P0Q3', 'CLIENTE', '(11) 96543-2109'),
(4, 'Lorena Vieira Marques', 'lorena.marques@gmail.com', '$2b$12$e8Y6V.oHq.oQ5u2oJ9C6vOGZ4H7Q4l5O0V1B3J4K5L6M7N8O9P0Q4', 'CLIENTE', '(11) 95432-1098');

INSERT INTO Categoria (id_categoria, nome, descricao) VALUES
(1, 'Pratos Executivos', 'Refeições completas individuais para almoço e jantar corporativo'),
(2, 'Massas Artesanais', 'Massas frescas de produção própria com molhos especiais'),
(3, 'Sobremesas', 'Doces finos, tortas e sobremesas em porções individuais'),
(4, 'Bebidas', 'Sucos naturais, refrigerantes e águas');

INSERT INTO Ingrediente (id_ingrediente, nome, unidade_medida, estoque_minimo) VALUES
(1, 'Filé de Peito de Frango', 'KG', 5.000),
(2, 'Arroz Branco Tipo 1', 'KG', 10.000),
(3, 'Feijão Carioca', 'KG', 5.000),
(4, 'Massa Espaguete Grano Duro', 'KG', 4.000),
(5, 'Molho de Tomate Pelado', 'KG', 6.000),
(6, 'Carne Moída Patinho', 'KG', 4.000),
(7, 'Óleo de Soja', 'L', 3.000),
(8, 'Queijo Parmesão Ralado', 'KG', 1.500);

INSERT INTO Prato (id_prato, id_categoria, nome, descricao, preco_venda, tempo_preparo_min, ativo) VALUES
(1, 1, 'Prato Feito Tradicional de Frango', 'Filé de frango grelhado acompanhado de arroz soltinho, feijão e tempero caseiro', 28.50, 20, TRUE),
(2, 2, 'Espaguete à Bolonhesa Clássico', 'Espaguete grano duro envolvido em molho artesanal de carne e queijo parmesão', 34.00, 25, TRUE),
(3, 1, 'Frango Grelhado Low Carb', 'Filé de frango temperado com ervas finas sem acompanhamentos pesados', 24.00, 15, TRUE);

INSERT INTO Composto_por (id_prato, id_ingrediente, qtd_necessaria) VALUES
(1, 1, 0.200),
(1, 2, 0.150),
(1, 3, 0.100),
(1, 7, 0.020),
(2, 4, 0.200),
(2, 6, 0.150),
(2, 5, 0.150),
(2, 8, 0.030),
(3, 1, 0.250),
(3, 7, 0.010);

INSERT INTO Lote_Estoque (id_lote, id_ingrediente, numero_lote, qtd_atual, custo_unit, data_entrada, data_validade) VALUES
(1, 1, 'LOTE-FR-20261101', 20.000, 18.5000, '2026-11-01 08:00:00', '2026-11-20'),
(2, 2, 'LOTE-AR-20261015', 50.000, 5.2000, '2026-10-15 09:30:00', '2027-04-15'),
(3, 3, 'LOTE-FE-20261020', 30.000, 7.8000, '2026-10-20 10:00:00', '2027-03-20'),
(4, 4, 'LOTE-ES-20261005', 15.000, 11.0000, '2026-10-05 11:00:00', '2027-08-05'),
(5, 5, 'LOTE-TM-20261010', 25.000, 8.9000, '2026-10-10 14:00:00', '2027-02-10'),
(6, 6, 'LOTE-CM-20261105', 12.000, 32.0000, '2026-11-05 07:45:00', '2026-11-18'),
(7, 7, 'LOTE-OL-20260901', 18.000, 6.5000, '2026-09-01 10:15:00', '2027-09-01'),
(8, 8, 'LOTE-PQ-20261028', 5.000, 65.0000, '2026-10-28 16:20:00', '2027-01-28');

INSERT INTO Movimento_Estoque (id_ingrediente, id_usuario, tipo_mov, qtd, data_hora, motivo) VALUES
(1, 1, 'ENTRADA', 20.000, '2026-11-01 08:00:00', 'Entrada inicial de mercadoria conforme NF 1042'),
(2, 1, 'ENTRADA', 50.000, '2026-10-15 09:30:00', 'Entrada mensal distribuidora cerealista');

INSERT INTO Bancada (id_bancada, cod_identificacao, descricao, valor_hora, valor_caucao, status_operacional) VALUES
(1, 'BANCADA-01', 'Estação quente com fogão industrial de 6 bocas, chapa e coifa de exaustão', 45.00, 300.00, 'DISPONIVEL'),
(2, 'BANCADA-02', 'Estação de panificação e massas com masseira, forno combinado e bancada de inox', 60.00, 500.00, 'DISPONIVEL'),
(3, 'BANCADA-03', 'Estação fria para montagem de saladas e sushis com pista refrigerada', 40.00, 200.00, 'DISPONIVEL');

INSERT INTO Reserva_Bancada (id_reserva, id_cliente, id_bancada, data_hora_inicio, data_hora_fim, valor_total_horas, valor_caucao_pago, valor_adicionais, status_reserva) VALUES
(1, 3, 2, '2026-11-10 08:00:00', '2026-11-10 13:00:00', 300.00, 500.00, 0.00, 'CONFIRMADA'),
(2, 3, 1, '2026-11-12 14:00:00', '2026-11-12 18:00:00', 180.00, 300.00, 0.00, 'SOLICITADA');