# %%
import pandas as pd
import requests
from dotenv import load_dotenv
import os

# %%
load_dotenv()
API_OMIE_BASE = "https://app.omie.com.br/api/v1/"
API_KEY_OMIE = os.getenv("API_KEY_OMIE")
API_SECRET_OMIE = os.getenv("API_SECRET_OMIE")
# %%
class Omie:
    def __init__(self, call: str, endpoint: str ):
        self.api_base = str(API_OMIE_BASE)
        self.app_key = API_KEY_OMIE
        self.app_secret = API_SECRET_OMIE
        self.call = call
        self.endpoint = endpoint
    
    def listar_clientes(self, page: int = 1):
        url = f"{self.api_base}{self.endpoint}"

        payload = {
            "call": self.call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [
                {
                    "pagina": page,
                    "registros_por_pagina": 100,
                    "apenas_importado_api": "N",
                    "exibir_caracteristicas": "S"
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        # Verifica erro HTTP
        response.raise_for_status()
        data = response.json()
        dataframe = pd.DataFrame(data['clientes_cadastro'])

        # Retorna JSON já convertido em dict
        return dataframe

# %%

omie_clientes = Omie(call="ListarClientes", endpoint="geral/clientes/")

# %%
print(omie_clientes.listar_clientes())
# %%
print(omie_clientes.listar_clientes().info())
# %%
