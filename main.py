import json
import time
from pathlib import Path
from datetime import datetime
import logging

from src.pipelines.collect_clientes import ClientesPipeline
from src.pipelines.collect_produtos import ProdutosPipeline
from src.pipelines.collect_vendedores import VendedoresPipeline
from src.pipelines.extract import (
    load_json_cliente,
    load_json_produtos,
    load_json_vendedores
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 📁 salvar JSON (padronizado)
def salvar_json(dados, nome):
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    path = Path("data/json_raw")
    path.mkdir(parents=True, exist_ok=True)

    file_path = path / f"{nome}_{data_hoje}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    logging.info(f"JSON salvo em: {file_path}")


# 🧠 execução genérica de pipeline
def executar_pipeline(nome, pipeline, loader):
    logging.info(f"Iniciando pipeline de {nome}")

    data = pipeline().run()

    salvar_json(data, nome)

    logging.info(f"Total de {nome}: {len(data)}")

    loader(data)

    logging.info(f"Pipeline de {nome} finalizado\n")


# 📋 menu
def menu():
    opcoes = {
        "1": ("clientes", ClientesPipeline, load_json_cliente),
        "2": ("produtos", ProdutosPipeline, load_json_produtos),
        "3": ("vendedores", VendedoresPipeline, load_json_vendedores),
        "5": ("todos", None, None),
    }

    while True:
        print("\n=== MENU ===")
        print("1 - Clientes")
        print("2 - Produtos")
        print("3 - Vendedores")
        print("5 - Todos")
        print("x - Sair")

        escolha = input("\nEscolha uma opção: ").strip().lower()

        if escolha == "x":
            print("Encerrando...")
            break

        elif escolha == "5":
            executar_pipeline("clientes", ClientesPipeline, load_json_cliente)
            time.sleep(5)
            executar_pipeline("produtos", ProdutosPipeline, load_json_produtos)
            time.sleep(5)
            executar_pipeline("vendedores", VendedoresPipeline, load_json_vendedores)

        elif escolha in opcoes:
            nome, pipeline, loader = opcoes[escolha]
            executar_pipeline(nome, pipeline, loader)

        else:
            print("❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()