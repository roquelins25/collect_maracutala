from src.core.omie_base import OmieBase

class ClientesPipeline:
    def run(self):
        collector = OmieBase(
            call="ListarClientes",
            endpoint="geral/clientes/",
            response_key="clientes_cadastro",
            extra_params={"exibir_caracteristicas": "S"}
        )

        return collector.coletar_dados()