-- Consultas SQLite para relatórios
SELECT COUNT(*) AS quantidade_pedidos, ROUND(COALESCE(SUM(total),0),2) AS faturamento FROM pedidos;
SELECT p.nome, SUM(i.quantidade) AS unidades_vendidas
FROM pedido_itens i JOIN pratos p ON p.id=i.prato_id
GROUP BY p.id ORDER BY unidades_vendidas DESC;
SELECT p.nome, e.quantidade FROM estoque_pratos e JOIN pratos p ON p.id=e.prato_id ORDER BY p.nome;
SELECT status, COUNT(*) AS quantidade FROM pedidos GROUP BY status;
