import sys
import time
import calendar
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

_HISTORICO_INICIO  = date(2025, 1, 1)   # ajuste conforme necessidade
_RATE_LIMIT_SLEEP  = 15                  # segundos entre chamadas mensais

_DEFAULT_ARGS = {
    "owner": "maracutala",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}


# ── Helpers ───────────────────────────────────────────────────────────────

def _gerar_meses(inicio: date, fim: date):
    """Gera tuplas (data_inicio, data_fim, label) mês a mês no formato Omie (DD/MM/YYYY)."""
    cursor = inicio.replace(day=1)
    while cursor <= fim:
        ultimo_dia = calendar.monthrange(cursor.year, cursor.month)[1]
        data_fim_mes = min(date(cursor.year, cursor.month, ultimo_dia), fim)
        yield (
            cursor.strftime("%d/%m/%Y"),       # formato Omie
            data_fim_mes.strftime("%d/%m/%Y"), # formato Omie
            cursor.strftime("%Y_%m"),           # label para task_id
        )
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)


# ── Callable ──────────────────────────────────────────────────────────────

def _run_pedidos_mes(data_inicio: str, data_fim: str) -> None:
    """Coleta, transforma e persiste pedidos de um mês específico."""
    data = PedidosPipeline().run(data_inicio=data_inicio, data_fim=data_fim)
    df   = load_json_pedidos(data)
    load_pedidos(df)
    time.sleep(_RATE_LIMIT_SLEEP)  # respeita rate-limit da API Omie


# ── DAG ───────────────────────────────────────────────────────────────────

with DAG(
    dag_id="maracutala_pedidos_historico",
    default_args=_DEFAULT_ARGS,
    description="Backfill histórico de tb_pedidos mês a mês — trigger manual",
    schedule=None,
    start_date=datetime(_HISTORICO_INICIO.year, _HISTORICO_INICIO.month, 1),
    catchup=False,
    tags=["maracutala", "pedidos", "historico"],
) as dag:

    tasks = []
    hoje  = date.today()

    for data_ini, data_fim, label in _gerar_meses(_HISTORICO_INICIO, hoje):
        t = PythonOperator(
            task_id=f"pedidos_{label}",
            python_callable=_run_pedidos_mes,
            op_kwargs={"data_inicio": data_ini, "data_fim": data_fim},
        )
        # Cadeia sequencial: aguarda mês anterior antes de coletar o próximo
        if tasks:
            tasks[-1] >> t
        tasks.append(t)
