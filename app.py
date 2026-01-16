import streamlit as st
import pandas as pd

from auth.auth import login
from core.clt import calcular_clt
from core.precificacao import precificar


# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="Simulador de Precificação CLT",
    layout="wide"
)

login()
if not st.session_state.get("logged", False):
    st.stop()

st.title("📊 Simulador de Precificação CLT")


# =====================================================
# IDENTIFICAÇÃO
# =====================================================
st.header("1️⃣ Identificação da Proposta")

c1, c2, c3 = st.columns(3)
cliente = c1.text_input("Cliente")
titulo_proposta = c2.text_input(
    "Título da proposta",
    "Simulação de Custos e Precificação"
)
validade = c3.text_input("Validade", "30 dias")


# =====================================================
# CARGOS
# =====================================================
st.header("2️⃣ Estrutura de Cargos")

if "cargos" not in st.session_state:
    st.session_state.cargos = []

with st.expander("Adicionar cargo"):
    a, b, c = st.columns(3)
    cargo_nome = a.text_input("Cargo")
    salario = b.number_input("Salário (R$)", min_value=0.0, step=100.0)
    qtd = c.number_input("Quantidade", min_value=1, step=1)

    if st.button("Adicionar cargo"):
        st.session_state.cargos.append({
            "Cargo": cargo_nome,
            "Salário": salario,
            "Quantidade": qtd
        })
        st.rerun()

if st.session_state.cargos:
    st.subheader("Cargos adicionados")
    for idx, cargo in enumerate(st.session_state.cargos):
        col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
        col1.write(cargo["Cargo"])
        col2.write(f"R$ {cargo['Salário']:,.2f}")
        col3.write(cargo["Quantidade"])
        if col4.button("🗑️", key=f"rem_{idx}"):
            st.session_state.cargos.pop(idx)
            st.rerun()
else:
    st.info("Nenhum cargo adicionado.")


# =====================================================
# PARÂMETROS FINANCEIROS
# =====================================================
st.header("3️⃣ Parâmetros Financeiros")

p1, p2 = st.columns(2)
vale_refeicao = p1.number_input(
    "Vale refeição por colaborador (R$)",
    value=600.0,
    step=50.0
)

margem_pct = p2.number_input(
    "Margem de lucro (%)",
    value=20.0,
    step=1.0
)

st.subheader("Regime Tributário")

regime_tributario = st.radio(
    "Selecione o regime tributário",
    [
        "Simples Nacional – 6%",
        "Simples Nacional – 11,20%",
        "Simples Nacional – 13,50%",
        "Lucro Presumido – 15,25%"
    ]
)


# =====================================================
# CÁLCULOS
# =====================================================
st.header("4️⃣ Resultados")

if st.button("Calcular Precificação"):
    if not st.session_state.cargos:
        st.error("Adicione ao menos um cargo.")
        st.stop()

    total_clt = 0.0
    custos_unitarios = {}

    for cargo in st.session_state.cargos:
        _, custo_unit = calcular_clt(cargo["Salário"], vale_refeicao)
        custos_unitarios[cargo["Cargo"]] = custo_unit
        total_clt += custo_unit * cargo["Quantidade"]

    margem = margem_pct / 100
    preco_sem_imposto = total_clt / (1 - margem)

    # -------- REGIME --------
    if regime_tributario == "Simples Nacional – 6%":
        aliquota_total = 0.06
        regime_nome = "Simples Nacional – 6%"
    elif regime_tributario == "Simples Nacional – 11,20%":
        aliquota_total = 0.112
        regime_nome = "Simples Nacional – 11,20%"
    elif regime_tributario == "Simples Nacional – 13,50%":
        aliquota_total = 0.135
        regime_nome = "Simples Nacional – 13,50%"
    else:
        aliquota_total = 0.1525
        regime_nome = "Lucro Presumido – 15,25%"

    imposto_total = preco_sem_imposto * aliquota_total
    preco_com_imposto = preco_sem_imposto + imposto_total
    lucro_total = preco_sem_imposto - total_clt

    # -------- COMPOSIÇÃO DOS IMPOSTOS --------
    COMPOSICAO_SIMPLES = {
        "IRPJ": 0.04,
        "CSLL": 0.035,
        "PIS": 0.028,
        "COFINS": 0.127,
        "CPP": 0.285,
        "ISS": 0.485
    }

    COMPOSICAO_LUCRO_PRESUMIDO = {
        "PIS": 0.0065,
        "COFINS": 0.03,
        "CSLL": 0.028,
        "IRPJ": 0.048,
        "ISS": 0.04
    }

    if regime_tributario.startswith("Simples"):
        impostos_detalhados = {
            nome: imposto_total * perc
            for nome, perc in COMPOSICAO_SIMPLES.items()
        }
    else:
        impostos_detalhados = {
            nome: preco_sem_imposto * perc
            for nome, perc in COMPOSICAO_LUCRO_PRESUMIDO.items()
        }

    # -------- RESUMO --------
    st.subheader("📌 Resumo Financeiro Consolidado")

    a, b, c, d = st.columns(4)
    a.metric("Custo CLT Total", f"R$ {total_clt:,.2f}")
    b.metric("Impostos Totais", f"R$ {imposto_total:,.2f}")
    c.metric("Lucro Total", f"R$ {lucro_total:,.2f}")
    d.metric("Valor da Nota Fiscal", f"R$ {preco_com_imposto:,.2f}")

    # -------- DETALHAMENTO POR CARGO --------
    st.header("📌 Detalhamento por Cargo")

    dados_cargos = []

    for cargo in st.session_state.cargos:
        qtd = cargo["Quantidade"]
        custo_unit = custos_unitarios[cargo["Cargo"]]
        custo_total_cargo = custo_unit * qtd
        proporcao = custo_total_cargo / total_clt

        impostos_cargo = {
            nome: valor * proporcao
            for nome, valor in impostos_detalhados.items()
        }

        total_imposto_cargo = sum(impostos_cargo.values())
        lucro_cargo = lucro_total * proporcao

        dados_cargos.append({
            "Cargo": cargo["Cargo"],
            "Quantidade": qtd,
            "Custo CLT Unitário (R$)": custo_unit,
            "Custo CLT Total (R$)": custo_total_cargo,
            "Impostos Total Cargo (R$)": total_imposto_cargo,
            "Lucro Total Cargo (R$)": lucro_cargo,
            "Lucro Unitário (R$)": lucro_cargo / qtd,
            "Preço Total Cargo (R$)": custo_total_cargo + total_imposto_cargo + lucro_cargo,
            "Preço Unitário (R$)": (custo_total_cargo + total_imposto_cargo + lucro_cargo) / qtd
        })

    df = pd.DataFrame(dados_cargos)
    st.dataframe(df, use_container_width=True)

    # -------- DETALHAMENTO DE IMPOSTOS POR CARGO --------
    st.subheader("📌 Detalhamento de Impostos por Cargo")

    for cargo in st.session_state.cargos:
        qtd = cargo["Quantidade"]
        custo_total_cargo = custos_unitarios[cargo["Cargo"]] * qtd
        proporcao = custo_total_cargo / total_clt

        impostos_cargo = {
            nome: valor * proporcao
            for nome, valor in impostos_detalhados.items()
        }

        with st.expander(f"📂 {cargo['Cargo']} — Impostos detalhados"):
            for nome, valor in impostos_cargo.items():
                st.write(f"- {nome}: R$ {valor:,.2f}")

            st.divider()
            st.write(
                f"**Total de Impostos do Cargo:** "
                f"R$ {sum(impostos_cargo.values()):,.2f}"
            )
