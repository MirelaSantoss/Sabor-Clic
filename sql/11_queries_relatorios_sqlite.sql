-- Resumo geral de vendas
SELECT
    COUNT(*) AS quantidade_pedidos,
    ROUND(COALESCE(SUM(total), 0), 2) AS faturamento
FROM pedidos;

-- pratos mais vendidos
SELECT
    p.nome,
    SUM(i.quantidade) AS unidades_vendidas
FROM pedido_itens i
JOIN pratos p ON p.id = i.prato_id
GROUP BY p.id
ORDER BY unidades_vendidas DESC;

-- estoque de pratos
SELECT
    p.nome,
    e.quantidade
FROM estoque_pratos e
JOIN pratos p ON p.id = e.prato_id
ORDER BY p.nome;

-- quantidade de pedidos em casa etapa
SELECT
    status,
    COUNT(*) AS quantidade
FROM pedidos
GROUP BY status;

-- Receita/faturamento por bancada
SELECT
    b.cod_identificacao,
    COUNT(r.id) AS total_reservas,
    ROUND(COALESCE(SUM(r.valor_total_horas + r.valor_adicionais), 0), 2) AS receita_bancada
FROM bancadas b
LEFT JOIN reservas_bancadas r ON r.bancada_id = b.id
GROUP BY b.id
ORDER BY receita_bancada DESC;
