import json
import os
from datetime import datetime

from src.pipelines.collect_clientes import ClientesPipeline
from src.pipelines.collect_produtos import ProdutosPipeline

def salvar_json(dados, nome):
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    path = f"data/json_raw/{nome}_{data_hoje}.json"

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    
    clientes = ClientesPipeline().run()
    salvar_json(clientes, "clientes")
    len_clientes = len(clientes)
    print(f"Total de clientes coletados: {len_clientes}")

    produtos = ProdutosPipeline().run()
    salvar_json(produtos, "produtos")
    len_produtos = len(produtos)
    print(f"Total de produtos coletados: {len_produtos}")   