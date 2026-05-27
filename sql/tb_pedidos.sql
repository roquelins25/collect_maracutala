-- tb_pedidos.sql
-- Cabeçalho dos pedidos de venda extraídos da API Omie.
-- PK: codigo_pedido

CREATE TABLE IF NOT EXISTS tb_pedidos (
    codigo_pedido               BIGINT          PRIMARY KEY,
    codigo_pedido_integracao    VARCHAR(100),
    data_previsao               DATE,
    codigo_cliente              BIGINT,
    codigo_vendedor             BIGINT,
    etapa                       VARCHAR(10),
    valor_total_pedido          NUMERIC(15, 2),
    qtde_parcelas               INT
);
