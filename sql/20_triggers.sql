USE sabor_e_clic;

DELIMITER $$

--desconto automatico de insumos usados em cada prato pedido por cliente
CREATE TRIGGER trg_baixa_estoque_item_pedido
AFTER INSERT ON Item_Pedido
FOR EACH ROW
BEGIN
    UPDATE Lote_Estoque le
    INNER JOIN Composto_por cp ON le.id_ingrediente = cp.id_ingrediente
    --GREATEST = impedir q o saldo de itens fique negativo
    SET le.qtd_atual = GREATEST(0.000, le.qtd_atual - (cp.qtd_necessaria * NEW.qtd))
    WHERE cp.id_prato = NEW.id_prato
      AND le.qtd_atual > 0.000;

    INSERT INTO Movimento_Estoque (
        id_ingrediente,
        id_usuario,
        tipo_mov,
        qtd,
        data_hora,
        motivo
    )
    SELECT 
        cp.id_ingrediente,
        p.id_cliente,
        'BAIXA_PEDIDO',
        (cp.qtd_necessaria * NEW.qtd),
        NOW(),
        CONCAT('Baixa automática gerada pelo Pedido #', NEW.id_pedido, ' - Prato ID ', NEW.id_prato)
    FROM Composto_por cp
    INNER JOIN Pedido p ON p.id_pedido = NEW.id_pedido
    WHERE cp.id_prato = NEW.id_prato;

END$$

-- atualiza o valor total do pedido a cada novo item q entrar no "carrinho"
CREATE TRIGGER trg_atualiza_valor_total_pedido
AFTER INSERT ON Item_Pedido
FOR EACH ROW
BEGIN
    UPDATE Pedido
    SET valor_total = (
        SELECT COALESCE(SUM(preco_unit * qtd), 0.00)
        FROM Item_Pedido
        WHERE id_pedido = NEW.id_pedido
    )
    WHERE id_pedido = NEW.id_pedido;
END$$

DELIMITER ;