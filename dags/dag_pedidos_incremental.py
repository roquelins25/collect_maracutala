import sys
from pathlib import Path
from datetime import datetime, timedelta, date

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.pipelines.extract import PedidosPipeline
from src.pipelines.transform import load_json_pedidos
from src.pipelines.load import load_pedidos

# ── Configurações ─────────────────────────────────────────────────────────

_JANELA_DIAS = 90   # quantos dias para trás a janela cobre

_DEFAULT_ARGS = {
    "owner": "maracutala",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}


# ── Callable ──────────────────────────────────────────────────────────────

def _run_pedidos_incremental() -> None:
    """
    Coleta pedidos dos últimos _JANELA_DIAS dias.
    O transform já filtra devolvidos/cancelados/faturados, por isso
    o DELETE + INSERT mantém a tabela sempre com o estado atual dos pedidos abertos.
    """
    hoje       = date.today()
    data_inicio = (hoje - timedelta(days=_JANELA_DIAS)).strftime("%d/%m/%Y")
    data_fim    = hoje.strftime("%d/%m/%Y")

    data = PedidosPipeline().run(data_inicio=data_inicio, data_fim=data_fim)
    df   = load_json_pedidos(data)
    load_pedidos(df)


# ── DAG ───────────────────────────────────────────────────────────────────

with DAG(
    dag_id="maracutala_pedidos_incremental",
    default_args=_DEFAULT_ARGS,
    description=f"Carga incremental de tb_pedidos — últimos {_JANELA_DIAS} dias, a cada 2 horas",
    schedule="0 */2 * * *",
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=["maracutala", "pedidos", "incremental"],
) as dag:

    PythonOperator(
        task_id=f"pedidos_ultimos_{_JANELA_DIAS}_dias",
        python_callable=_run_pedidos_incremental,
    )
