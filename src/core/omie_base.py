import requests
import logging
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.config import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class OmieBase:
    def __init__(self, call, endpoint, response_key, extra_params=None):
        logging.info(f"Inicializando OmieBase para call: {call}")
        settings = Settings()

        self.api_base = settings.API_OMIE_BASE
        self.app_key = settings.API_KEY_OMIE
        self.app_secret = settings.API_SECRET_OMIE

        self.call = call
        self.endpoint = endpoint
        self.response_key = response_key
        self.extra_params = extra_params or {}

        retry = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        logging.info("OmieBase inicializado com sucesso")

    def _make_request(self, payload):
        url = f"{self.api_base}{self.endpoint}"

        response = self.session.post(url, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        if "faultstring" in data:
            raise Exception(data["faultstring"])

        return data

    def _build_payload(self, page):
        logging.info(f"Construindo payload para página {page}")
        base = {
            "pagina": page,
            "registros_por_pagina": 100,
            "apenas_importado_api": "N"            
        }

        base.update(self.extra_params)
        logging.debug(f"Payload construído: {base}")

        return {
            "call": self.call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [base]
        }

    def coletar_dados(self):
        logging.info(f"Iniciando coleta de dados para {self.call}")
        payload = self._build_payload(1)

        first = self._make_request(payload)
        total_paginas = first.get("total_de_paginas", 1)

        all_data = []

        pbar = tqdm(range(1, total_paginas + 1), desc="Coletando páginas")

        for page in pbar:
            payload["param"][0]["pagina"] = page

            data = self._make_request(payload)
            registros = data.get(self.response_key, [])

            all_data.extend(registros)

            # atualiza texto da barra
            pbar.set_postfix({
                "pagina": page,
                "registros": len(registros)
            })

        return all_data