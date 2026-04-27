# %%
import os
import json
import logging
import pandas as pd
import requests

from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import Settings

# %%
# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# %%
# Configurações
settings = Settings()

API_OMIE_BASE = settings.API_OMIE_BASE
API_KEY_OMIE = settings.API_KEY_OMIE
API_SECRET_OMIE = settings.API_SECRET_OMIE
API_HEADERS = {"Content-Type": "application/json"}

# %%
class Omie:
    def __init__(self, call: str, endpoint: str):
        self.api_base = API_OMIE_BASE
        self.app_key = API_KEY_OMIE
        self.app_secret = API_SECRET_OMIE
        self.headers = API_HEADERS
        self.call = call
        self.endpoint = endpoint

        # Retry robusto
        retry_strategy = Retry(
            total=5,
            connect=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    def _make_request(self, payload: dict):
        url = f"{self.api_base}{self.endpoint}"

        response = self.session.post(
            url,
            json=payload,
            headers=self.headers,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        # Tratamento de erro da API Omie
        if "faultstring" in data:
            raise Exception(f"Erro na API Omie: {data['faultstring']}")

        return data

    def total_paginas(self) -> int:
        logging.info("Calculando total de páginas...")

        payload = self._base_payload(page=1)
        data = self._make_request(payload)

        total = data.get("total_de_paginas", 1)

        logging.info(f"Total de páginas: {total}")
        return total

    def _base_payload(self, page: int) -> dict:
        return {
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


    def coletar_dados(self) -> list:
        logging.info("Iniciando coleta de dados...")

        total_paginas = self.total_paginas()
        all_data = []

        payload = self._base_payload(page=1)

        for page in range(1, total_paginas + 1):
            logging.info(f"Coletando página {page}/{total_paginas}...")

            payload["param"][0]["pagina"] = page

            data = self._make_request(payload)

            clientes = data.get("clientes_cadastro", [])
            all_data.extend(clientes)

        logging.info(f"Coleta finalizada. Total de registros: {len(all_data)}")
        return all_data
    
    def process(self, name:str):
        logging.info(f"Iniciando processo de coleta para {name}...")
        dados = self.coletar_dados()
        datahoje = datetime.now().strftime("%Y-%m-%d")
        path_json = f'../data/json/{name}_{datahoje}.json'

        with open(path_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        logging.info(f"Dados salvos em {path_json}")

