USE sabor_e_clic;

SELECT 
    DATE(p.data_hora) AS data_venda,
    COUNT(DISTINCT p.id_pedido) AS total_pedidos,
    SUM(p.valor_total) AS faturamento_bruto,
    ROUND(AVG(p.valor_total), 2) AS ticket_medio
FROM Pedido p
WHERE p.status_pedido NOT IN ('CANCELADO')
GROUP BY DATE(p.data_hora)
ORDER BY data_venda DESC;

SELECT 
    i.id_ingrediente,
    i.nome AS ingrediente,
    i.unidade_medida,
    i.estoque_minimo,
    COALESCE(SUM(le.qtd_atual), 0.000) AS estoque_disponivel,
    CASE 
        WHEN COALESCE(SUM(le.qtd_atual), 0.000) = 0 THEN 'ESGOTADO'
        WHEN COALESCE(SUM(le.qtd_atual), 0.000) <= i.estoque_minimo THEN 'COMPRA URGENTE'
        ELSE 'REGULAR'
    END AS status_abastecimento
FROM Ingrediente i
LEFT JOIN Lote_Estoque le ON i.id_ingrediente = le.id_ingrediente
GROUP BY i.id_ingrediente, i.nome, i.unidade_medida, i.estoque_minimo
HAVING estoque_disponivel <= i.estoque_minimo
ORDER BY estoque_disponivel ASC;

SELECT 
    pr.id_prato,
    pr.nome AS nome_prato,
    c.nome AS categoria,
    pr.preco_venda,
    ROUND(SUM(cp.qtd_necessaria * sub.custo_medio), 2) AS custo_producao_estimado,
    ROUND(pr.preco_venda - SUM(cp.qtd_necessaria * sub.custo_medio), 2) AS lucro_bruto_porcao,
    CONCAT(ROUND(((pr.preco_venda - SUM(cp.qtd_necessaria * sub.custo_medio)) / pr.preco_venda) * 100, 1), '%') AS margem_lucro_pct
FROM Prato pr
INNER JOIN Categoria c ON pr.id_categoria = c.id_categoria
INNER JOIN Composto_por cp ON pr.id_prato = cp.id_prato
INNER JOIN (
    SELECT id_ingrediente, AVG(custo_unit) AS custo_medio
    FROM Lote_Estoque
    GROUP BY id_ingrediente
) sub ON cp.id_ingrediente = sub.id_ingrediente
GROUP BY pr.id_prato, pr.nome, c.nome, pr.preco_venda
ORDER BY lucro_bruto_porcao DESC;

SELECT 
    b.cod_identificacao,
    b.descricao,
    b.valor_hora,
    COUNT(rb.id_reserva) AS total_locacoes,
    COALESCE(SUM(TIMESTAMPDIFF(HOUR, rb.data_hora_inicio, rb.data_hora_fim)), 0) AS total_horas_utilizadas,
    COALESCE(SUM(rb.valor_total_horas + rb.valor_adicionais), 0.00) AS receita_total_gerada
FROM Bancada b
LEFT JOIN Reserva_Bancada rb ON b.id_bancada = rb.id_bancada AND rb.status_reserva IN ('CONFIRMADA', 'CONCLUIDA')
GROUP BY b.id_bancada, b.cod_identificacao, b.descricao, b.valor_hora
ORDER BY receita_total_gerada DESC;