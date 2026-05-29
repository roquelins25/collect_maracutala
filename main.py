# %%
import logging

from src.pipelines.extract import (
    ClientesPipeline,
    PedidosPipeline,
    ProdutosPipeline,
    VendedoresPipeline,
    NotaFiscalPipeline
)
from src.pipelines.transform import (
    load_json_cliente,
    load_json_pedidos,
    load_json_produtos,
    load_json_vendedores,
    load_json_notas_fiscais
)
from src.pipelines.load import process_table

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
        loader(result)

    logging.info("── Pipeline %s finalizado ──\n", nome)
    return result


# %%
# ── Dimensões ─────────────────────────────────────────────────────────────

df_clientes = executar_pipeline(
    "clientes",
    ClientesPipeline,
    transformer=load_json_cliente,
    loader=lambda df: process_table("tb_clientes", df),
)
# %%
df_produtos = executar_pipeline(
    "produtos",
    ProdutosPipeline,
    transformer=load_json_produtos,
    loader=lambda df: process_table("tb_produtos", df),
)
# %%
df_vendedores = executar_pipeline(
    "vendedores",
    VendedoresPipeline,
    transformer=load_json_vendedores,
    loader=lambda df: process_table("tb_vendedores", df),
)
# %%
# ── Pedidos (informe o período desejado) ──────────────────────────────────

DATA_INICIO = "01/01/2026"
DATA_FIM    = "31/01/2026"
# %%
pedidos_result = executar_pipeline(
    "pedidos",
    PedidosPipeline,
    transformer=load_json_pedidos,
    loader=lambda df: process_table("tb_pedidos", df),
    data_inicio=DATA_INICIO,
    data_fim=DATA_FIM,
)

# %%
nf_result = executar_pipeline(
    "notas_fiscais",
    NotaFiscalPipeline,
    transformer=load_json_notas_fiscais,
    loader=lambda df: process_table("tb_nf", df),
    data_inicio=DATA_INICIO,
    data_fim=DATA_FIM
)
# %%
len(nf_result)
# %%
nf_result.head()
# %%
nf_result.info()
# %%
print(nf_result.columns)
# %%
