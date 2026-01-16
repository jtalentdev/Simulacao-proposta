# core/precificacao.py

def precificar(custo_total: float, margem: float):
    """
    custo_total : custo total (CLT + impostos)
    margem      : margem de lucro (ex: 0.2 para 20%)

    Retorna:
    - preco_final
    - lucro_total
    """
    if margem >= 1:
        raise ValueError("Margem deve ser menor que 100%")

    preco_final = custo_total / (1 - margem)
    lucro_total = preco_final - custo_total
    return preco_final, lucro_total
