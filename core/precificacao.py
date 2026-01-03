# =====================================================
# Precificação (Cost Plus)
# =====================================================

def precificar(custo: float, margem: float):
    """
    Calcula o preço de venda e o lucro com base no modelo Cost Plus.

    :param custo: Custo total (ex: custo CLT consolidado)
    :param margem: Margem de lucro desejada (ex: 0.20 para 20%)
    :return:
        - preco: preço de venda sem impostos
        - lucro: valor absoluto do lucro
    """
    if margem >= 1:
        raise ValueError("A margem deve ser menor que 100% (1.0)")

    preco = custo / (1 - margem)
    lucro = preco - custo

    return preco, lucro
