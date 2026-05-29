import sys
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.pipelines.extract import ClientesPipeline, ProdutosPipeline, VendedoresPipeline
from src.pipelines.transform import load_json_cliente, load_json_produtos, load_json_vendedores
from src.pipelines.load import load_clientes, load_produtos, load_vendedores

_DEFAULT_ARGS = {
    "owner": "maracutala",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}


# ── Callables ─────────────────────────────────────────────────────────────

def _run_clientes() -> None:
    data = ClientesPipeline().run()
    df   = load_json_cliente(data)
    load_clientes(df)


def _run_produtos() -> None:
    data = ProdutosPipeline().run()
    df   = load_json_produtos(data)
    load_produtos(df)


def _run_vendedores() -> None:
    data = VendedoresPipeline().run()
    df   = load_json_vendedores(data)
    load_vendedores(df)


# ── DAG ───────────────────────────────────────────────────────────────────

with DAG(
    dag_id="maracutala_dimensoes",
    default_args=_DEFAULT_ARGS,
    description="Carga das dimensões Maracutala a cada 4 horas",
    schedule="0 */4 * * *",
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=["maracutala", "dimensoes"],
) as dag:

    op_clientes   = PythonOperator(task_id="tb_clientes",   python_callable=_run_clientes)
    op_produtos   = PythonOperator(task_id="tb_produtos",   python_callable=_run_produtos)
    op_vendedores = PythonOperator(task_id="tb_vendedores", python_callable=_run_vendedores)

    # Dimensões são independentes — executam em paralelo
    [op_clientes, op_produtos, op_vendedores]
