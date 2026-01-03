# =====================================================
# Cálculo de custos CLT
# =====================================================

# Encargos CLT considerados no modelo
# Percentuais aplicados sobre o salário base
ENCARGOS = {
    "INSS Patronal": 0.20,
    "RAT": 0.01,
    "FGTS": 0.08,
    "FGTS adicional": 0.032,
    "13º salário": 0.0833,
    "Férias": 0.1111,
    "1/3 constitucional": 0.037
}


def calcular_clt(salario: float, beneficio: float):
    """
    Calcula o custo CLT detalhado de um colaborador.

    :param salario: Salário base mensal
    :param beneficio: Benefício mensal (ex: vale refeição)
    :return:
        - detalhes: dict com valor de cada encargo
        - custo_total: custo total mensal do colaborador
    """
    detalhes = {}
    total_encargos = 0.0

    for nome, perc in ENCARGOS.items():
        valor = salario * perc
        detalhes[nome] = valor
        total_encargos += valor

    custo_total = salario + total_encargos + beneficio
    return detalhes, custo_total
