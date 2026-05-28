CREATE TABLE IF NOT EXISTS tb_pedidos (
    numped                BIGINT          NOT NULL,
    codcli                BIGINT,
    datprev               DATE,
    codpro                BIGINT,
    cfop                  VARCHAR(255),
    qtd                   DECIMAL(10, 2),
    valor_deducao         DECIMAL(10, 2),
    valor_desconto        DECIMAL(10, 2),
    valor_icms_desonerado DECIMAL(10, 2),
    valor_mercadoria      DECIMAL(10, 2),
    valor_total           DECIMAL(10, 2),
    valor_unitario        DECIMAL(10, 2),
    codvend               BIGINT,
    codigo_categoria      VARCHAR(50),   -- código hierárquico Omie: "1.01.01"
    cancelado             VARCHAR(10),
    devolvido             VARCHAR(10),
    dinc                  DATE,
    faturado              VARCHAR(10),
    hinc                  TIME,
    codcatitem            VARCHAR(50),   -- código hierárquico ou numérico
    codimposto            VARCHAR(50)    -- código de cenário de impostos
);
