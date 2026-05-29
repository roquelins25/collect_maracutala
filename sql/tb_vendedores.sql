CREATE TABLE IF NOT EXISTS tb_vendedores (
    codigo              BIGINT  PRIMARY KEY,
    comissao            varchar(10),          
    fatura_pedido       VARCHAR(10),
    inativo             VARCHAR(10),
    nome                VARCHAR(255),
    visualiza_pedido    VARCHAR(10),
    email               VARCHAR(255)
);
