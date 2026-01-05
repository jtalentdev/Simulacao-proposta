import streamlit as st
import pandas as pd

# ================= AUTH =================
from auth.auth import login

# ================= CORE =================
from core.clt import calcular_clt
from core.precificacao import precificar

# ================= IA =================
from core.ia_textos import gerar_resumo_executivo, gerar_texto_comercial

# ================= RELATÓRIOS =================
from core.relatorios import gerar_proposta_comercial_pdf, gerar_pdf_tecnico

# ================= CONFIG =================
st.set_page_config(
    page_title="Simulador de Precificação CLT",
    layout="wide"
)

# ================= LOGIN =================
login()
if not st.session_state.get("logged", False):
    st.stop()

st.title("📊 Simulador de Precificação CLT")

# =====================================================
# UTIL – PREVIEW (REGRA A)
# =====================================================
def render_texto_preview(texto: str):
    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha:
            st.markdown("")
        elif linha.startswith("**") and linha.endswith("**"):
            st.markdown(f"### {linha.replace('**', '').strip()}")
        else:
            st.markdown(linha)

# =====================================================
# 1️⃣ IDENTIFICAÇÃO
# =====================================================
st.header("1️⃣ Identificação da Proposta")

c1, c2, c3 = st.columns(3)
cliente = c1.text_input("Cliente")
titulo_proposta = c2.text_input(
    "Título da proposta",
    "Proposta Comercial: Fornecimento de Mão de Obra Especializada"
)
validade = c3.text_input("Validade", "30 dias")

# =====================================================
# 2️⃣ CARGOS
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

        if col4.button("🗑️", key=f"remover_{idx}"):
            st.session_state.cargos.pop(idx)
            st.rerun()
else:
    st.info("Nenhum cargo adicionado.")

# =====================================================
# 3️⃣ PARÂMETROS FINANCEIROS
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
        "Simples Nacional – Anexo III (21%)",
        "Lucro Real (18%)"
    ]
)

# =====================================================
# 4️⃣ CONTEÚDO DA PROPOSTA (IA)
# =====================================================
st.header("4️⃣ Conteúdo da Proposta (IA)")

contexto = st.text_area(
    "Contexto da proposta",
    height=120,
    placeholder="Descreva o escopo, cliente e objetivos..."
)

TOM_PADRAO = "executivo, comercial, voltado ao setor farmacêutico"

x1, x2 = st.columns(2)
if x1.button("Gerar Resumo Executivo"):
    st.session_state.resumo_exec = gerar_resumo_executivo(contexto, TOM_PADRAO)

if x2.button("Gerar Texto Comercial"):
    st.session_state.texto_comercial = gerar_texto_comercial(contexto, TOM_PADRAO)

resumo_exec = st.text_area(
    "Resumo Executivo (editável)",
    st.session_state.get("resumo_exec", ""),
    height=200
)

texto_comercial = st.text_area(
    "Texto Comercial (editável)",
    st.session_state.get("texto_comercial", ""),
    height=260
)

# =====================================================
# PREVIEW
# =====================================================
st.subheader("📌 Pré-visualização – Resumo Executivo")
render_texto_preview(resumo_exec)

st.subheader("📌 Pré-visualização – Texto Comercial")
render_texto_preview(texto_comercial)

# =====================================================
# 5️⃣ CÁLCULOS
# =====================================================
st.header("5️⃣ Resultados")

if st.button("Calcular Precificação"):
    if not st.session_state.cargos:
        st.error("Adicione ao menos um cargo.")
        st.stop()

    # ---------- CLT ----------
    total_custo_clt = 0

    for cargo in st.session_state.cargos:
        _, custo_unit = calcular_clt(
            cargo["Salário"],
            vale_refeicao
        )
        total_custo_clt += custo_unit * cargo["Quantidade"]

    margem = margem_pct / 100
    preco_sem_imposto = total_custo_clt / (1 - margem)

    # ---------- IMPOSTOS ----------
    if regime_tributario.startswith("Simples"):
        regime_nome = "Simples Nacional – Anexo III"
        aliquota_total = 0.21
        impostos_base = {
            "IRPJ": 0.04,
            "CSLL": 0.035,
            "PIS": 0.028,
            "COFINS": 0.127,
            "CPP": 0.285,
            "ISS": 0.485
        }
        valor_total_imposto = preco_sem_imposto * aliquota_total
        impostos_detalhados = {
            nome: valor_total_imposto * perc
            for nome, perc in impostos_base.items()
        }
    else:
        regime_nome = "Lucro Real"
        aliquota_total = 0.18
        impostos_base = {
            "IRPJ": 0.06,
            "CSLL": 0.035,
            "PIS": 0.02,
            "COFINS": 0.05,
            "CPRB": 0.015
        }
        valor_total_imposto = preco_sem_imposto * aliquota_total
        impostos_detalhados = {
            nome: preco_sem_imposto * perc
            for nome, perc in impostos_base.items()
        }

    lucro_total = preco_sem_imposto - total_custo_clt
    preco_final = preco_sem_imposto + valor_total_imposto

    st.session_state.resultado = {
        "custos": {
            "clt_total": total_custo_clt
        },
        "precificacao": {
            "preco_sem_imposto": preco_sem_imposto,
            "preco_com_imposto": preco_final,
            "lucro": lucro_total,
            "margem": margem
        },
        "impostos": {
            "regime": regime_nome,
            "aliquota_total": aliquota_total,
            "valor_total": valor_total_imposto,
            "detalhado": impostos_detalhados
        }
    }

# =====================================================
# 6️⃣ EXIBIÇÃO DOS RESULTADOS
# =====================================================
if "resultado" in st.session_state:
    r = st.session_state.resultado

    st.subheader("📌 Resumo Financeiro Consolidado")

    a, b, c, d = st.columns(4)
    a.metric("Custo CLT Total", f"R$ {r['custos']['clt_total']:,.2f}")
    b.metric("Impostos Totais", f"R$ {r['impostos']['valor_total']:,.2f}")
    c.metric("Lucro Total", f"R$ {r['precificacao']['lucro']:,.2f}")
    d.metric("Valor da Nota Fiscal", f"R$ {r['precificacao']['preco_com_imposto']:,.2f}")

    # =================================================
    # DETALHAMENTO POR CARGO
    # =================================================
    st.header("📌 Detalhamento por Cargo")

    dados_cargos = []

    for cargo in st.session_state.cargos:
        detalhes, custo_unit = calcular_clt(
            cargo["Salário"],
            vale_refeicao
        )

        qtd = cargo["Quantidade"]
        custo_total_cargo = custo_unit * qtd
        proporcao = custo_total_cargo / r["custos"]["clt_total"]

        impostos_cargo = {
            nome: valor * proporcao
            for nome, valor in r["impostos"]["detalhado"].items()
        }

        total_imposto_cargo = sum(impostos_cargo.values())
        lucro_cargo = r["precificacao"]["lucro"] * proporcao

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

    df_cargos = pd.DataFrame(dados_cargos)
    st.dataframe(df_cargos, use_container_width=True)

    # =================================================
    # DETALHAMENTO DE IMPOSTOS POR CARGO
    # =================================================
    st.subheader("📌 Detalhamento de Impostos por Cargo")

    for cargo in st.session_state.cargos:
        detalhes, custo_unit = calcular_clt(
            cargo["Salário"],
            vale_refeicao
        )

        qtd = cargo["Quantidade"]
        custo_total_cargo = custo_unit * qtd
        proporcao = custo_total_cargo / r["custos"]["clt_total"]

        impostos_cargo = {
            nome: valor * proporcao
            for nome, valor in r["impostos"]["detalhado"].items()
        }

        with st.expander(f"📂 {cargo['Cargo']} — Impostos detalhados"):
            for nome, valor in impostos_cargo.items():
                st.write(f"- {nome}: R$ {valor:,.2f}")

            st.divider()
            st.write(
                f"**Total de Impostos do Cargo:** "
                f"R$ {sum(impostos_cargo.values()):,.2f}"
            )

    # =================================================
    # RELATÓRIOS (PDF)
    # =================================================
    st.header("📄 Relatórios")

    c1, c2 = st.columns(2)

    if c1.button("Proposta Comercial (PDF)"):
        gerar_proposta_comercial_pdf(
            "proposta_comercial.pdf",
            cliente,
            titulo_proposta,
            resumo_exec,
            "",
            texto_comercial,
            validade,
            f"R$ {r['precificacao']['preco_com_imposto']:,.2f}",
            f"{margem_pct}%",
            st.session_state.cargos
        )
        with open("proposta_comercial.pdf", "rb") as f:
            st.download_button(
                "⬇️ Baixar Proposta Comercial",
                f,
                "proposta_comercial.pdf"
            )

    if c2.button("Proposta Técnica (PDF)"):
        gerar_pdf_tecnico(
            "proposta_tecnica.pdf",
            st.session_state.cargos,
            {},
            r["impostos"]["valor_total"],
            r["precificacao"]["lucro"],
            r["impostos"]["detalhado"]
        )
        with open("proposta_tecnica.pdf", "rb") as f:
            st.download_button(
                "⬇️ Baixar Proposta Técnica",
                f,
                "proposta_tecnica.pdf"
            )
