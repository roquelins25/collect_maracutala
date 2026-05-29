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

def load_json_pedidos(data: list) -> pd.DataFrame:

    logging.info("Processando pedidos (%d registros)", len(data))

    rows = []

    for pedido in data:

        # ── níveis principais ─────────────────────────────
        cab = pedido.get("cabecalho", {})
        info = pedido.get("infoCadastro", {})
        info_add = pedido.get("informacoes_adicionais", {})

        # lista de itens
        dets = pedido.get("det", [])

        for det in dets:

            produto = det.get("produto", {})
            inf_adic = det.get("inf_adic", {})

            rows.append({

                # ── cabeçalho ───────────────────────────
                "codigo_cliente": cab.get("codigo_cliente"),
                "data_previsao": cab.get("data_previsao"),
                "numero_pedido": cab.get("numero_pedido"),

                # ── produto ─────────────────────────────
                "cfop": produto.get("cfop"),
                "codigo_produto": produto.get("codigo_produto"),
                "quantidade": produto.get("quantidade"),
                "valor_deducao": produto.get("valor_deducao"),
                "valor_desconto": produto.get("valor_desconto"),
                "valor_icms_desonerado": produto.get("valor_icms_desonerado"),
                "valor_mercadoria": produto.get("valor_mercadoria"),
                "valor_total": produto.get("valor_total"),
                "valor_unitario": produto.get("valor_unitario"),

                # ── informações adicionais ──────────────
                "codVend": info_add.get("codVend"),
                "codigo_categoria": info_add.get("codigo_categoria"),

                # ── info cadastro ───────────────────────
                "cancelado": info.get("cancelado"),
                "devolvido": info.get("devolvido"),
                "dInc": info.get("dInc"),
                "faturado": info.get("faturado"),
                "hInc": info.get("hInc"),

                # ── info item ───────────────────────────
                "codigo_categoria_item": inf_adic.get("codigo_categoria_item"),
                "codigo_cenario_impostos_item": inf_adic.get("codigo_cenario_impostos_item"),
            })

    # ── DataFrame ───────────────────────────────────────
    df = pd.DataFrame(rows)

    # ── Conversão de tipos ──────────────────────────────
    df["data_previsao"] = pd.to_datetime(
        df["data_previsao"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    df["dInc"] = pd.to_datetime(
        df["dInc"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    numeric_cols = [
        "valor_unitario",
        "quantidade",
        "valor_total",
        "valor_mercadoria"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── filtros ─────────────────────────────────────────

    # filtro cenário impostos
    df = df[
        df["codigo_cenario_impostos_item"].isin([
            "3883521325",
            "4150250660"
        ])
    ]

    # remove cliente
    df = df[
        df["codigo_cliente"].astype(str) != "3955092831"
    ]

    # remove devolvidos/cancelados/faturados
    df = df[
        (df["devolvido"] == "N") &
        (df["cancelado"] == "N") &
        (df["faturado"] == "N")
    ]

    logging.info(
        "Pedidos processados: %d linhas, %d colunas",
        *df.shape
    )

    return df



def load_json_notas_fiscais(data: list) -> pd.DataFrame:

    logging.info(
        "Processando notas fiscais (%d registros)",
        len(data)
    )

    rows = []

    for nf in data:

        # ── níveis principais ─────────────────────────────
        compl = nf.get("compl", {})
        ide = nf.get("ide", {})
        dest = nf.get("nfDestInt", {})
        pedido = nf.get("pedido", {})
        total = nf.get("total", {})

        icms_tot = total.get("ICMSTot", {})

        dets = nf.get("det", [])

        for det in dets:

            nf_prod = det.get("nfProdInt", {})
            prod = det.get("prod", {})

            rows.append({

                # ── compl ───────────────────────────────
                "chave_nfe": compl.get("cChaveNFe"),
                "codigo_categoria": compl.get("cCodCateg"),

                # ── produto integração ──────────────────
                "codigo_item": nf_prod.get("nCodItem"),
                "codigo_produto": nf_prod.get("nCodProd"),

                # ── produto ─────────────────────────────
                "cfop": prod.get("CFOP"),
                "quantidade": prod.get("qCom"),
                "valor_produto": prod.get("vProd"),
                "valor_total_item": prod.get("vTotItem"),

                # ── ide ─────────────────────────────────
                "denegada": ide.get("cDeneg"),
                "data_cancelamento": ide.get("dCan"),
                "data_emissao": ide.get("dEmi"),
                "finalidade_nfe": ide.get("finNFe"),
                "numero_nf": ide.get("nNF"),
                "tipo_nf": ide.get("tpNF"),

                # ── destinatário ───────────────────────
                "codigo_cliente": dest.get("nCodCli"),

                # ── pedido ─────────────────────────────
                "devolvido": pedido.get("cDevolvido"),
                "numero_pedido": pedido.get("cNumPedido"),
                "codigo_vendedor": pedido.get("nIdVendedor"),
                "operacao_pedido": pedido.get("opPedido"),

                # ── total ──────────────────────────────
                "valor_nf": icms_tot.get("vNF")
            })

    # ── dataframe ───────────────────────────────────────
    df = pd.DataFrame(rows)

    # ── conversões ──────────────────────────────────────

    # datas
    date_cols = [
        "data_emissao",
        "data_cancelamento"
    ]

    for col in date_cols:

        df[col] = pd.to_datetime(
            df[col],
            format="%d/%m/%Y",
            errors="coerce"
        )

    # numéricos
    numeric_cols = [
        "quantidade",
        "valor_produto",
        "valor_total_item",
        "valor_nf",
        "codigo_item",
        "codigo_produto",
        "codigo_cliente",
        "codigo_vendedor"
    ]

    for col in numeric_cols:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # ── filtros ─────────────────────────────────────────

    # somente saída
    df = df[
        df["tipo_nf"] == "1"
    ]

    # remove devolvidos
    df = df[
        df["devolvido"] == "N"
    ]

    logging.info(
        "Notas fiscais processadas: %d linhas, %d colunas",
        *df.shape
    )

    return df
