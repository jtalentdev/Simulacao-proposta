import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader

# =====================================================
# CONFIGURAÇÕES GERAIS
# =====================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

MARGEM_ESQ = 2.5 * cm
MARGEM_DIR = 2.5 * cm
MARGEM_SUP = 2.5 * cm
MARGEM_INF = 3.0 * cm

LARGURA_UTIL = PAGE_WIDTH - (MARGEM_ESQ + MARGEM_DIR)

ALTURA_CABECALHO = 4.0 * cm
ESPACO_APOS_LINHA = 28  # dois espaçamentos

styles = getSampleStyleSheet()
STYLE_TEXTO = styles["Normal"]
STYLE_TEXTO.fontName = "Helvetica"
STYLE_TEXTO.fontSize = 11
STYLE_TEXTO.leading = 15

STYLE_TITULO = styles["Heading2"]
STYLE_TITULO.fontName = "Helvetica-Bold"
STYLE_TITULO.fontSize = 12
STYLE_TITULO.spaceAfter = 12

# =====================================================
# CONTEXTO DE PÁGINA
# =====================================================

def _novo_contexto(c, cliente, validade):
    y_inicio_corpo = PAGE_HEIGHT - MARGEM_SUP - ALTURA_CABECALHO - ESPACO_APOS_LINHA
    return {
        "c": c,
        "pagina": 1,
        "y": y_inicio_corpo,
        "cliente": cliente,
        "validade": validade,
    }

# =====================================================
# CABEÇALHO COMERCIAL
# =====================================================

def _cabecalho_comercial(ctx):
    c = ctx["c"]
    cliente = ctx["cliente"]
    validade = ctx["validade"]

    y_topo = PAGE_HEIGHT - MARGEM_SUP

    # Logo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "..", "assets", "logo.png")

    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(
            logo,
            MARGEM_ESQ,
            y_topo - ALTURA_CABECALHO + 0.5 * cm,
            width=3.2 * cm,
            height=3.2 * cm,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Texto à direita
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(
        PAGE_WIDTH - MARGEM_DIR,
        y_topo - 0.5 * cm,
        "PROPOSTA COMERCIAL",
    )

    c.setFont("Helvetica", 11)
    c.drawRightString(
        PAGE_WIDTH - MARGEM_DIR,
        y_topo - 1.6 * cm,
        cliente,
    )

    c.drawRightString(
        PAGE_WIDTH - MARGEM_DIR,
        y_topo - 2.6 * cm,
        f"Validade: {validade}",
    )

    # Linha horizontal
    y_linha = y_topo - ALTURA_CABECALHO
    c.line(MARGEM_ESQ, y_linha, PAGE_WIDTH - MARGEM_DIR, y_linha)

# =====================================================
# RODAPÉ COMERCIAL
# =====================================================

def _rodape_comercial(ctx, total_paginas):
    c = ctx["c"]
    pagina = ctx["pagina"]

    c.setFont("Helvetica", 9)
    c.drawRightString(
        PAGE_WIDTH - MARGEM_DIR,
        MARGEM_INF - 0.4 * cm,
        f"{pagina} / {total_paginas}",
    )

    c.line(
        MARGEM_ESQ,
        MARGEM_INF,
        PAGE_WIDTH - MARGEM_DIR,
        MARGEM_INF,
    )

    c.setFont("Helvetica", 8)
    c.drawCentredString(
        PAGE_WIDTH / 2,
        MARGEM_INF - 1.0 * cm,
        "J Talent Empreendimentos | Proposta Comercial | "
        "Contato: +55 (38) 9 8422 4399 | E-mail: contato@jtalent.com.br",
    )

# =====================================================
# NOVA PÁGINA COMERCIAL
# =====================================================

def _nova_pagina_comercial(ctx):
    c = ctx["c"]
    c.showPage()
    ctx["pagina"] += 1
    _cabecalho_comercial(ctx)
    ctx["y"] = PAGE_HEIGHT - MARGEM_SUP - ALTURA_CABECALHO - ESPACO_APOS_LINHA

# =====================================================
# DESENHO DE BLOCO DE TEXTO (COM QUEBRA)
# =====================================================

def _desenhar_bloco(ctx, texto):
    c = ctx["c"]

    p = Paragraph(texto.replace("\n", "<br/>"), STYLE_TEXTO)
    w, h = p.wrap(LARGURA_UTIL, ctx["y"])

    if ctx["y"] - h < MARGEM_INF:
        _nova_pagina_comercial(ctx)

    p.drawOn(c, MARGEM_ESQ, ctx["y"] - h)
    ctx["y"] -= h + 12

# =====================================================
# DESENHO DE TÍTULO DE BLOCO
# =====================================================

def _desenhar_titulo(ctx, titulo):
    c = ctx["c"]

    p = Paragraph(titulo, STYLE_TITULO)
    w, h = p.wrap(LARGURA_UTIL, ctx["y"])

    if ctx["y"] - h < MARGEM_INF:
        _nova_pagina_comercial(ctx)

    p.drawOn(c, MARGEM_ESQ, ctx["y"] - h)
    ctx["y"] -= h

# =====================================================
# RELATÓRIO COMERCIAL (FINAL)
# =====================================================

def gerar_proposta_comercial_pdf(
    caminho,
    cliente,
    _titulo_proposta,
    resumo_exec,
    _texto_inst,
    texto_comercial,
    validade,
    valor_mensal,
    _margem,
    _cargos,
):
    c = canvas.Canvas(caminho, pagesize=A4)

    ctx = _novo_contexto(c, cliente, validade)
    _cabecalho_comercial(ctx)

    # -------- Corpo --------
    _desenhar_titulo(ctx, "<b>Resumo Executivo</b>")
    _desenhar_bloco(ctx, resumo_exec)

    _desenhar_titulo(ctx, "<b>Resumo Comercial</b>")
    _desenhar_bloco(ctx, texto_comercial)

    # Valores
    valor_mensal_float = float(
        valor_mensal.replace("R$", "").replace(".", "").replace(",", ".")
    )

    _desenhar_titulo(ctx, "<b>Valores do Contrato</b>")
    _desenhar_bloco(
        ctx,
        f"Valor mensal do contrato: <b>R$ {valor_mensal_float:,.2f}</b><br/>"
        f"Valor anual do contrato (12 meses): "
        f"<b>R$ {(valor_mensal_float * 12):,.2f}</b>",
    )

    # -------- Finalização --------
    total_paginas = ctx["pagina"]
    for p in range(1, total_paginas + 1):
        c.showPage()

    c = canvas.Canvas(caminho, pagesize=A4)
    ctx = _novo_contexto(c, cliente, validade)
    _cabecalho_comercial(ctx)

    _desenhar_titulo(ctx, "<b>Resumo Executivo</b>")
    _desenhar_bloco(ctx, resumo_exec)
    _desenhar_titulo(ctx, "<b>Resumo Comercial</b>")
    _desenhar_bloco(ctx, texto_comercial)
    _desenhar_titulo(ctx, "<b>Valores do Contrato</b>")
    _desenhar_bloco(
        ctx,
        f"Valor mensal do contrato: <b>R$ {valor_mensal_float:,.2f}</b><br/>"
        f"Valor anual do contrato (12 meses): "
        f"<b>R$ {(valor_mensal_float * 12):,.2f}</b>",
    )

    _rodape_comercial(ctx, ctx["pagina"])
    c.save()

# =====================================================
# PROPOSTA TÉCNICA (VERSÃO CONGELADA)
# =====================================================

def gerar_pdf_tecnico(
    caminho_pdf,
    cargos,
    clt_detalhado,
    das_total,
    lucro,
    das_detalhado
):

    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4

    margem_esq = 2.5 * cm
    margem_dir = 2.5 * cm
    y = altura - 3 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margem_esq, y, "PROPOSTA TÉCNICA")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem_esq, y, "Custos por Cargo")
    y -= 20

    c.setFont("Helvetica", 11)
    for cargo in cargos:
        linha = (
            f"{cargo['Cargo']} | "
            f"Qtd: {cargo['Quantidade']} | "
            f"Salário Base: R$ {cargo['Salário']:,.2f}"
        )
        c.drawString(margem_esq, y, linha)
        y -= 16

        if y < 3 * cm:
            c.showPage()
            y = altura - 3 * cm

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem_esq, y, f"Lucro Mensal Total: R$ {lucro:,.2f}")

    c.save()
