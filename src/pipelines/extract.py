# %% 
import json
import pandas as pd
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# %%
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(f"Diretório base: {BASE_DIR}")
# %%
def save_parquet(df, file_name):
    path = BASE_DIR / "data" / "parquet" / "bronze"
    path.mkdir(parents=True, exist_ok=True)

    file_path = path / file_name

    df.to_parquet(file_path, index=False)

    logging.info(f"Arquivo salvo em: {file_path}")
# %%
def load_json_cliente(data):
    logging.info("Processando dados de clientes")
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
        'caracteristicas', 
        'tipo_atividade'
        ]

    df = df[[col for col in columns if col in df.columns]]

    save_parquet(df, 'clientes.parquet')
    logging.info("Dados de clientes processados e salvos em parquet")
    return df

# %%
def load_json_produtos(data):
    produtos = pd.DataFrame(data)
    logging.info("Processando dados de produtos")

    columns_produtos = [
            'codigo_produto', 
            'codigo_produto_integracao',
            'descricao', 
            'bloqueado',
            'bloquear_exclusao', 
            'caracteristicas', 
            'cest', 
            'cfop',
            'class_trib',
            'codInt_familia', 
            'codigo',
            'codigo_familia',
            'ean',
            'inativo', 
            'marca', 
            'modelo', 
            'tipoItem',
            'unidade', 
            'valor_unitario'
            ]

    df = produtos[[col for col in columns_produtos if col in produtos.columns]]

    save_parquet(df, 'produtos.parquet')
    logging.info("Dados de produtos processados e salvos em parquet")
    return df
