-- Triggers SQLite instaladas automaticamente por app.db.criar_tabelas().
CREATE TRIGGER IF NOT EXISTS conferir_estoque_antes_pedido
BEFORE INSERT ON pedido_itens
WHEN EXISTS (SELECT 1 FROM estoque_pratos WHERE prato_id = NEW.prato_id)
BEGIN
 SELECT CASE WHEN (SELECT quantidade FROM estoque_pratos WHERE prato_id=NEW.prato_id)<NEW.quantidade
 THEN RAISE(ABORT, 'Estoque insuficiente') END;
END;
CREATE TRIGGER IF NOT EXISTS baixar_estoque_pedido AFTER INSERT ON pedido_itens
BEGIN
 UPDATE estoque_pratos SET quantidade=quantidade-NEW.quantidade WHERE prato_id=NEW.prato_id;
END;
CREATE TRIGGER IF NOT EXISTS registrar_status AFTER UPDATE OF status ON pedidos
WHEN NEW.status <> OLD.status
BEGIN
 INSERT INTO historico_status(pedido_id,status) VALUES (NEW.id,NEW.status);
END;
