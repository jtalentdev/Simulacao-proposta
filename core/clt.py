# core/clt.py

ENCARGOS_CLT = {
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
    Retorna:
    - detalhes dos encargos
    - custo total unitário CLT (salário + encargos + benefício)
    """
    detalhes = {}
    total_encargos = 0.0

    for nome, perc in ENCARGOS_CLT.items():
        valor = salario * perc
        detalhes[nome] = valor
        total_encargos += valor

    custo_total_unitario = salario + total_encargos + beneficio
    return detalhes, custo_total_unitario
