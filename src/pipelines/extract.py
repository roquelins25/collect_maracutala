from src.core.omie_base import OmieBase

class ClientesPipeline:
    def run(self):
        collector = OmieBase(
            call="ListarClientes",
            endpoint="geral/clientes/",
            response_key="clientes_cadastro",
            extra_params={"exibir_caracteristicas": "S",
                          "apenas_importado_api": "N"}
        )

        return collector.coletar_dados()
    
class PedidosPipeline:
    def run(self, data_inicio=None, data_fim=None):
        if not data_inicio or not data_fim:
            raise ValueError("Informe data_inicio e data_fim")
        
        print(f"Coletando pedidos de {data_inicio} a {data_fim}...")

        collector = OmieBase(
            call="ListarPedidos",
            endpoint="produtos/pedido/",
            response_key="pedido_venda_produto",
            extra_params={
                "data_previsao_de": data_inicio,
                "data_previsao_ate": data_fim
            }
        )

        return collector.coletar_dados()

class ProdutosPipeline:
    def run(self):
        collector = OmieBase(
            call="ListarProdutos",
            endpoint="geral/produtos/",
            response_key="produto_servico_cadastro",
            extra_params={"exibir_caracteristicas": "S",
                          "apenas_importado_api": "N",
                          "filtrar_apenas_omiepdv": "N"}
        )

        return collector.coletar_dados()
    
class VendedoresPipeline:
    def run(self):
        collector = OmieBase(
            call="ListarVendedores",
            endpoint="geral/vendedores/",
            response_key="cadastro"
        )

        return collector.coletar_dados()
    