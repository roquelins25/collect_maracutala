from src.core.omie_base import OmieBase

class ProdutosPipeline:
    def run(self):
        collector = OmieBase(
            call="ListarProdutos",
            endpoint="geral/produtos/",
            response_key="produto_servico_cadastro",
            extra_params={"filtrar_apenas_omiepdv": "N"}
        )

        return collector.coletar_dados()