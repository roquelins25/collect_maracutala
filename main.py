# %%
import logging
import pandas as pd
from datetime import datetime

from src.pipelines.extract import (
    ClientesPipeline,
    PedidosPipeline,
    ProdutosPipeline,
    VendedoresPipeline,
)
from src.pipelines.transform import (
    load_json_cliente,
    load_json_pedidos,
    load_json_produtos,
    load_json_vendedores,
)
from src.pipelines.load import (
    load_clientes,
    load_pedidos,
    load_produtos,
    load_vendedores,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# %%
# ── Executor genérico ─────────────────────────────────────────────────────

def executar_pipeline(nome, pipeline, transformer=None, loader=None, **kwargs):
    logging.info("── Iniciando pipeline: %s ──", nome)

    data = pipeline().run(**kwargs)
    logging.info("Total extraído de %s: %d registros", nome, len(data))

    result = data
    if transformer:
        result = transformer(data)

    if loader and result is not None:
        # load_pedidos recebe (df_cabecalho, df_itens)
        if isinstance(result, tuple):
            loader(*result)
        else:
            loader(result)

    logging.info("── Pipeline %s finalizado ──\n", nome)
    return result


# %%
# ── Dimensões ─────────────────────────────────────────────────────────────

df_clientes = executar_pipeline(
    "clientes",
    ClientesPipeline,
    transformer=load_json_cliente,
    loader=load_clientes,
)
# %%
df_produtos = executar_pipeline(
    "produtos",
    ProdutosPipeline,
    transformer=load_json_produtos,
    loader=load_produtos
)
#%%
df_vendedores = executar_pipeline(
    "vendedores",
    VendedoresPipeline,
    transformer=load_json_vendedores,
    loader=load_vendedores
)
# %%
# ── Pedidos (informe o período desejado) ──────────────────────────────────

DATA_INICIO = "01/01/2025"
DATA_FIM    = datetime.today().strftime("%d/%m/%Y")

pedidos_result = executar_pipeline(
    "pedidos",
    PedidosPipeline,
    transformer=load_json_pedidos,
    loader=load_pedidos,
    data_inicio=DATA_INICIO,
    data_fim=DATA_FIM,
)

