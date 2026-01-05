import streamlit as st
import pandas as pd

from auth.auth import login
from core.clt import calcular_clt
from core.precificacao import precificar
from core.ia_textos import gerar_resumo_executivo, gerar_texto_comercial
from core.relatorios import gerar_proposta_comercial_pdf


# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Simulador de Precificação CLT",
    layout="wide"
)

if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    login()
    st.stop()


# =====================================================
# CABEÇALHO
# =====================================================

st.title("📊 Simulador de Precificação CLT – Proposta Comercial")


# =====================================================
# DADOS DA PROPOSTA
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    cliente = st.text_input("Cliente")

with col2:
    titulo_proposta = st.text_input(
        "Título da Proposta",
        value="Proposta Comercial para Fornecimento de Mão de Obra Especializada"
    )

with col3:
    validade = st.date_input("Validade da Proposta")


# =====================================================
# REGIME TRIBUTÁRIO
# =====================================================

st.subheader("🏛️ Regime Tributário")

regime = st.radio(
    "Selecione o regime tributário",
    [
        "Simples Nacional – Anexo III (21%)",
        "Lucro Real (18%)"
    ]
)

aliquota_imposto = 0.21 if "Simples" in regime else 0.18


# =====================================================
# PARÂMETROS
# =====================================================

st.subheader("⚙️ Parâmetros Gerais")

col1, col2 = st.columns(2)

with col1:
    vale_refeicao = st.number_input(
        "Vale Refeição Mensal (R$)",
        min_value=0.0,
        value=600.0,
        step=50.0
    )

with col2:
    margem_lucro = st.slider(
        "Margem de Lucro (%)",
        min_value=5,
        max_value=50,
        value=20
    ) / 100


# =====================================================
# CARGOS
# =====================================================

st.subheader("👥 Cargos")

if "cargos" not in st.session_state:
    st.session_state.cargos = []

with st.form("form_cargo"):
    col1, col2, col3 = st.columns(3)

    with col1:
        nome_cargo = st.text_input("Cargo")

    with col2:
        salario = st.number_input("Salário (R$)", min_value=0.0, step=500.0)

    with col3:
        quantidade = st.number_input("Quantidade", min_value=1, step=1)

    if st.form_submit_button("Adicionar Cargo"):
        st.session_state.cargos.append({
            "Cargo": nome_cargo,
            "Salário": salario,
            "Quantidade": quantidade
        })

if st.session_state.cargos:
    st.dataframe(pd.DataFrame(st.session_state.cargos), use_container_width=True)


# =====================================================
# CÁLCULOS
# =====================================================

if st.session_state.cargos:

    total_clt = 0.0

    # Custo CLT total
    for cargo in st.session_state.cargos:
        _, custo_unit = calcular_clt(
            cargo["Salário"],
            vale_refeicao
        )
        total_clt += custo_unit * cargo["Quantidade"]

    # Impostos totais conforme regime
    total_impostos = total_clt * aliquota_imposto

    # Precificação
    preco_total, lucro_total = precificar(
        total_clt + total_impostos,
        margem_lucro
    )

    # =================================================
    # DETALHAMENTO POR CARGO (CONGELADO)
    # =================================================

    dados_cargos = []

    for cargo in st.session_state.cargos:
        _, custo_unit = calcular_clt(
            cargo["Salário"],
            vale_refeicao
        )

        qtd = cargo["Quantidade"]
        custo_total_cargo = custo_unit * qtd
        proporcao = custo_total_cargo / total_clt if total_clt else 0

        imposto_cargo = total_impostos * proporcao
        lucro_cargo = lucro_total * proporcao

        dados_cargos.append({
            "Cargo": cargo["Cargo"],
            "Quantidade": qtd,
            "Custo CLT Unitário (R$)": custo_unit,
            "Custo CLT Total (R$)": custo_total_cargo,
            "Impostos Total Cargo (R$)": imposto_cargo,
            "Lucro Total Cargo (R$)": lucro_cargo,
            "Lucro Unitário (R$)": lucro_cargo / qtd,
            "Preço Total Cargo (R$)": custo_total_cargo + imposto_cargo + lucro_cargo,
            "Preço Unitário (R$)": (custo_total_cargo + imposto_cargo + lucro_cargo) / qtd
        })

    st.session_state.dados_cargos = dados_cargos

    st.subheader("📌 Detalhamento por Cargo")
    st.dataframe(pd.DataFrame(dados_cargos), use_container_width=True)

    st.metric("Valor mensal da NF", f"R$ {preco_total:,.2f}")
    st.metric("Valor anual da NF", f"R$ {(preco_total * 12):,.2f}")


# =====================================================
# TEXTOS DA PROPOSTA (IA)
# =====================================================

st.subheader("📝 Textos da Proposta")

if "resumo_exec" not in st.session_state:
    st.session_state.resumo_exec = ""

if "texto_comercial" not in st.session_state:
    st.session_state.texto_comercial = ""

col1, col2 = st.columns(2)

with col1:
    if st.button("Gerar Resumo Executivo"):
        st.session_state.resumo_exec = gerar_resumo_executivo(
            contexto=cliente,
            tom="executivo"
        )

    resumo_exec = st.text_area(
        "Resumo Executivo",
        value=st.session_state.resumo_exec,
        height=260
    )

with col2:
    if st.button("Gerar Texto Comercial"):
        st.session_state.texto_comercial = gerar_texto_comercial(
            contexto=cliente,
            tom="comercial"
        )

    texto_comercial = st.text_area(
        "Resumo Comercial",
        value=st.session_state.texto_comercial,
        height=260
    )


# =====================================================
# GERAR PDF
# =====================================================

st.subheader("📄 Gerar Proposta Comercial")

if st.button("Gerar PDF"):
    gerar_proposta_comercial_pdf(
        "proposta_comercial.pdf",
        cliente,
        titulo_proposta,
        resumo_exec,
        "",
        texto_comercial,
        validade.strftime("%d/%m/%Y"),
        f"R$ {preco_total:,.2f}",
        margem_lucro,
        st.session_state.dados_cargos
    )

    with open("proposta_comercial.pdf", "rb") as f:
        st.download_button(
            "⬇️ Baixar Proposta Comercial",
            f,
            file_name="proposta_comercial.pdf",
            mime="application/pdf"
        )
