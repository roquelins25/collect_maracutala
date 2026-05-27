# %%
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ── Clientes ──────────────────────────────────────────────────────────────

def load_json_cliente(data: list) -> pd.DataFrame:
    logging.info("Processando dados de clientes (%d registros)", len(data))
    df = pd.DataFrame(data)

    columns = [
        'codigo_cliente_integracao',
        'codigo_cliente_omie',
        'nome_fantasia',
        'pessoa_fisica',
        'razao_social',
        'bairro',
        'estado',
        'cep',
        'cidade',
        'cnpj_cpf',
        'complemento',
        'inativo',
        'inscricao_estadual',
        'inscricao_municipal',
        'tipo_atividade',
        'recomendacoes',
    ]

    df = df[[col for col in columns if col in df.columns]]
    # Extrai codigo_vendedor do campo aninhado
    df['codigo_vendedor'] = df['recomendacoes'].apply(
        lambda x: x.get('codigo_vendedor') if isinstance(x, dict) else None
    )
    df.drop(columns=['recomendacoes'], inplace=True, errors='ignore')

    logging.info("Clientes processados: %d linhas, %d colunas", *df.shape)
    return df


# ── Produtos ──────────────────────────────────────────────────────────────

def load_json_produtos(data: list) -> pd.DataFrame:
    logging.info("Processando dados de produtos (%d registros)", len(data))
    df = pd.DataFrame(data)

    columns = [
        'codigo_produto',
        'codigo_produto_integracao',
        'descricao',
        'bloqueado',
        'bloquear_exclusao',
        'caracteristicas',
        'cest',
        'cfop',
        'class_trib',
        'codigo',
        'codigo_familia',
        'descricao_familia',
        'ean',
        'inativo',
        'marca',
        'modelo',
        'tipoItem',             
        'unidade',
        'valor_unitario',
    ]

    df = df[[col for col in columns if col in df.columns]]

    # Padroniza para snake_case
    df = df.rename(columns={
                        'tipoItem':'tipo_item'
    })
    
    def extrair_sabor(x):

        if isinstance(x, dict):
            return x.get('cConteudo')

        if isinstance(x, list) and len(x) > 0:

            primeiro = x[0]

            if isinstance(primeiro, dict):
                return primeiro.get('cConteudo')

        return None
    
    df['sabor'] = df['caracteristicas'].apply(extrair_sabor)

    df.drop(columns=['caracteristicas'], inplace=True, errors='ignore')

    logging.info("Produtos processados: %d linhas, %d colunas", *df.shape)
    return df


# ── Vendedores ────────────────────────────────────────────────────────────

def load_json_vendedores(data: list) -> pd.DataFrame:
    logging.info("Processando dados de vendedores (%d registros)", len(data))
    df = pd.DataFrame(data)

    columns = [
        'codigo',
        'comissao',
        'email',
        'fatura_pedido',
        'inativo',
        'nome',
        'visualiza_pedido',
    ]

    df = df[[col for col in columns if col in df.columns]]

    logging.info("Vendedores processados: %d linhas, %d colunas", *df.shape)
    return df


# ── Pedidos ───────────────────────────────────────────────────────────────

def load_json_pedidos(data: list) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Transforma a lista bruta de pedidos em dois DataFrames:
      - df_cabecalho : um registro por pedido (→ tb_pedidos)
      - df_itens     : um registro por item de pedido (→ tb_pedidos_itens)

    Retorna (df_cabecalho, df_itens).
    """
    logging.info("Processando dados de pedidos (%d registros)", len(data))

    cabecalhos = []
    itens = []

    for pedido in data:
        cab  = pedido.get("cabecalho", {})
        dets = pedido.get("det", [])

        cabecalhos.append({
            "codigo_pedido":            cab.get("codigo_pedido"),
            "codigo_pedido_integracao": cab.get("codigo_pedido_integracao"),
            "data_previsao":            _parse_date_br(cab.get("data_previsao")),
            "codigo_cliente":           cab.get("codigo_cliente"),
            "codigo_vendedor":          cab.get("codigo_vendedor"),
            "etapa":                    cab.get("etapa"),
            "valor_total_pedido":       cab.get("valor_total_pedido"),
            "qtde_parcelas":            cab.get("qtde_parcelas"),
        })

        for num, det in enumerate(dets, start=1):
            prod = det.get("produto", {})
            itens.append({
                "codigo_pedido":     cab.get("codigo_pedido"),
                "item_num":          num,
                "codigo_produto":    prod.get("codigo_produto"),
                "descricao_produto": prod.get("descricao"),
                "quantidade":        prod.get("quantidade"),
                "valor_unitario":    prod.get("valor_unitario"),
                "valor_total_item":  prod.get("valor_total"),
            })

    df_cabecalho = pd.DataFrame(cabecalhos)
    df_itens     = pd.DataFrame(itens)

    logging.info(
        "Pedidos processados: %d cabeçalhos, %d itens",
        len(df_cabecalho), len(df_itens),
    )
    return df_cabecalho, df_itens


# ── Helpers ───────────────────────────────────────────────────────────────

def _parse_date_br(date_str: str | None):
    if not date_str:
        return None
    try:
        return pd.to_datetime(date_str, dayfirst=True).date()
    except Exception:
        return None
