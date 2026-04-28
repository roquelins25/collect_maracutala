from src.core.omie_base import OmieBase

class VendedoresPipeline:
    def run(self):
        collector = OmieBase(
            call="ListarVendedores",
            endpoint="geral/vendedores/",
            response_key="cadastro"
        )

        return collector.coletar_dados()