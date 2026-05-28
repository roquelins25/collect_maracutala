CREATE TABLE IF NOT EXISTS tb_clientes (
    codigo_cliente_omie         BIGINT PRIMARY KEY,
    codigo_cliente_integracao   BIGINT,
    nome_fantasia               VARCHAR(255),
    pessoa_fisica               VARCHAR(10),
    razao_social                VARCHAR(255),
    bairro                      VARCHAR(100),
    estado                      VARCHAR(2),
    cep                         VARCHAR(10),
    cidade                      VARCHAR(100),
    cnpj_cpf                    VARCHAR(20),
    complemento                 VARCHAR(255),
    inativo                     VARCHAR(10),
    inscricao_estadual          VARCHAR(50),
    inscricao_municipal         VARCHAR(50),
    tipo_atividade              VARCHAR(100),
    codigo_vendedor             BIGINT
);
