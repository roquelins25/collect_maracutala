"""
load.py — Camada de persistência: recebe DataFrames já transformados e os
salva no PostgreSQL (credenciais no .env).

Fluxo por tabela dimensão:  upsert via tabela temporária + COPY + INSERT … ON CONFLICT
Fluxo itens de pedido:      DELETE por codigo_pedido + COPY (bulk insert)
"""

import csv
import json
import logging
from io import StringIO
from pathlib import Path

import pandas as pd

from src.config.conectDB import connect_db

logger = logging.getLogger(__name__)

# ── Diretório com os arquivos DDL ─────────────────────────────────────────
# load.py está em  src/pipelines/  →  ../..  é a raiz do projeto
_SQL_DIR = Path(__file__).resolve().parent.parent.parent / "sql"

# ── Chave primária de cada tabela dimensão ────────────────────────────────
_TABLE_PK = {
    "tb_clientes":      "codigo_cliente_omie",
    "tb_produtos":      "codigo_produto",
    "tb_vendedores":    "codigo",
    "tb_pedidos":       "codigo_pedido",
}

# ── Renomeio de colunas antes de persistir (camelCase → snake_case) ───────
_COLUMN_RENAME = {
    "tb_produtos": {
        "tipoItem":"tipo_item",
    }
}


# ── Utilitários ───────────────────────────────────────────────────────────

def _create_table_if_not_exists(conn, table: str) -> None:
    """Executa o DDL do arquivo sql/<table>.sql, se existir."""
    sql_path = _SQL_DIR / f"{table}.sql"
    if not sql_path.exists():
        logger.warning("DDL não encontrado para '%s' em %s — tabela não será criada", table, _SQL_DIR)
        return
    with open(sql_path, encoding="utf-8") as f:
        ddl = f.read()
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()
    logger.info("Tabela '%s' verificada/criada.", table)


def _serialize_complex_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas com list/dict para JSON string (compatível com TEXT/JSONB no PG)."""
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(
                lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
            )
    return df


def _fix_float_integers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.select_dtypes(include="float64").columns:
        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue
        if (non_null % 1 == 0).all():          
            df[col] = df[col].astype(pd.Int64Dtype())
    return df


def _to_csv_buffer(df: pd.DataFrame) -> StringIO:
    buf = StringIO()
    df.to_csv(buf, index=False, header=False, quoting=csv.QUOTE_MINIMAL)
    buf.seek(0)
    return buf


# ── Estratégias de escrita ────────────────────────────────────────────────

def _upsert_dimensao(conn, df: pd.DataFrame, table: str, pk_col: str) -> None:
    df = _serialize_complex_cols(df)
    df = _fix_float_integers(df)

    # Remove linhas com PK nula (não podem ser inseridas)
    before = len(df)
    df = df.dropna(subset=[pk_col])
    dropped = before - len(df)
    if dropped:
        logger.warning("%s: %d linha(s) descartada(s) por PK nula em '%s'", table, dropped, pk_col)

    if df.empty:
        logger.warning("%s: DataFrame vazio após filtro de PK — nada a persistir.", table)
        return

    cols     = df.columns.tolist()
    cols_q   = ", ".join(f'"{c}"' for c in cols)        
    tmp      = f"tmp_{table}"
    upd_set  = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in cols if c != pk_col)

    copy_sql   = f'COPY {tmp} ({cols_q}) FROM STDIN WITH (FORMAT CSV, NULL \'\')'
    upsert_sql = f"""
        INSERT INTO {table} ({cols_q})
        SELECT {cols_q} FROM {tmp}
        ON CONFLICT ("{pk_col}") DO UPDATE SET {upd_set}
    """

    with conn.cursor() as cur:
        cur.execute(
            f'CREATE TEMP TABLE {tmp} (LIKE {table} INCLUDING DEFAULTS) ON COMMIT DROP'
        )
        cur.copy_expert(copy_sql, _to_csv_buffer(df))
        cur.execute(upsert_sql)

    conn.commit()
    logger.info("%s: %d registro(s) upserted (PK: %s)", table, len(df), pk_col)


def _delete_insert_pedidos_itens(conn, df: pd.DataFrame) -> None:

    df = _serialize_complex_cols(df)
    df = _fix_float_integers(df)
    table = "tb_pedidos_itens"

    pedido_ids = df["codigo_pedido"].dropna().unique().tolist()
    if not pedido_ids:
        logger.warning("tb_pedidos_itens: nenhum codigo_pedido válido — abortando.")
        return

    cols   = df.columns.tolist()
    cols_q = ", ".join(f'"{c}"' for c in cols)
    copy_sql   = f'COPY {table} ({cols_q}) FROM STDIN WITH (FORMAT CSV, NULL \'\')'
    delete_sql = f'DELETE FROM {table} WHERE codigo_pedido = ANY(%s)'

    with conn.cursor() as cur:
        cur.execute(delete_sql, (pedido_ids,))
        deleted = cur.rowcount
        cur.copy_expert(copy_sql, _to_csv_buffer(df))

    conn.commit()
    logger.info(
        "tb_pedidos_itens: %d item(ns) deletado(s), %d inserido(s) — %d pedido(s)",
        deleted, len(df), len(pedido_ids),
    )


# ── Função genérica ───────────────────────────────────────────────────────

def process_table(table: str, df: pd.DataFrame) -> None:
    rename_map = _COLUMN_RENAME.get(table, {})
    if rename_map:
        df = df.rename(columns=rename_map)

    conn = connect_db()
    try:
        _create_table_if_not_exists(conn, table)

        if table == "tb_pedidos_itens":
            _delete_insert_pedidos_itens(conn, df)
        else:
            if table not in _TABLE_PK:
                raise ValueError(f"Tabela '{table}' não está mapeada em _TABLE_PK")
            _upsert_dimensao(conn, df, table, _TABLE_PK[table])

    except Exception:
        conn.rollback()
        logger.exception("Falha ao processar tabela '%s'", table)
        raise
    finally:
        conn.close()


# ── Funções públicas por entidade ─────────────────────────────────────────

def load_clientes(df: pd.DataFrame) -> None:
    process_table("tb_clientes", df)


def load_produtos(df: pd.DataFrame) -> None:
    process_table("tb_produtos", df)


def load_vendedores(df: pd.DataFrame) -> None:
    process_table("tb_vendedores", df)


def load_pedidos(df_cabecalho: pd.DataFrame, df_itens: pd.DataFrame) -> None:
    process_table("tb_pedidos", df_cabecalho)
    process_table("tb_pedidos_itens", df_itens)
