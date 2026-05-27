-- tb_pedidos_itens.sql
-- Itens de pedido de venda extraídos da API Omie.
-- Estratégia de carga: DELETE por codigo_pedido + INSERT (sem upsert individual).

CREATE TABLE IF NOT EXISTS tb_pedidos_itens (
    codigo_pedido       BIGINT          NOT NULL,
    item_num            INT             NOT NULL,   -- sequência dentro do pedido (1, 2, 3…)
    codigo_produto      BIGINT,
    descricao_produto   VARCHAR(500),
    quantidade          NUMERIC(15, 4),
    valor_unitario      NUMERIC(15, 4),
    valor_total_item    NUMERIC(15, 2),
    PRIMARY KEY (codigo_pedido, item_num)
);
