import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# =====================================================
# CONFIGURAÇÕES
# =====================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

MARGEM_ESQ = 2.5 * cm
MARGEM_DIR = 2.5 * cm
MARGEM_SUP = 2.5 * cm
MARGEM_INF = 2.5 * cm

ALTURA_CABECALHO = 4.0 * cm
ALTURA_RODAPE = 2.2 * cm

LIMITE_INFERIOR = MARGEM_INF + ALTURA_RODAPE
LARGURA_UTIL = PAGE_WIDTH - (MARGEM_ESQ + MARGEM_DIR)

styles = getSampleStyleSheet()

STYLE_TEXTO = styles["Normal"]
STYLE_TEXTO.fontName = "Helvetica"
STYLE_TEXTO.fontSize = 11
STYLE_TEXTO.leading = 15

STYLE_TITULO = styles["Heading2"]
STYLE_TITULO.fontName = "Helvetica-Bold"
STYLE_TITULO.fontSize = 12
STYLE_TITULO.spaceAfter = 10

STYLE_CABECALHO = styles["Normal"]
STYLE_CABECALHO.fontName = "Helvetica-Bold"
STYLE_CABECALHO.fontSize = 14
STYLE_CABECALHO.leading = 16

# =====================================================
# CONTEXTO
# =====================================================

def _novo_contexto(c, cliente, validade, titulo):
    return {
        "c": c,
        "pagina": 1,
        "y": PAGE_HEIGHT - MARGEM_SUP - ALTURA_CABECALHO - 25,
        "cliente": cliente,
        "validade": validade,
        "titulo": titulo,
    }

# =====================================================
# CABEÇALHO (CONGELADO)
# =====================================================

def _cabecalho_comercial(ctx):
    c = ctx["c"]
    y_top = PAGE_HEIGHT - MARGEM_SUP

    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "..", "assets", "logo.png")

    if os.path.exists(logo_path):
        c.drawImage(
            ImageReader(logo_path),
            MARGEM_ESQ,
            y_top - ALTURA_CABECALHO + 0.6 * cm,
            width=3.2 * cm,
            height=3.2 * cm,
            preserveAspectRatio=True,
            mask="auto",
        )

    p = Paragraph(ctx["titulo"], STYLE_CABECALHO)
    w, h = p.wrap(LARGURA_UTIL - 4 * cm, ALTURA_CABECALHO)
    p.drawOn(
        c,
        PAGE_WIDTH - MARGEM_DIR - w,
        y_top - 0.8 * cm - h
    )

    c.setFont("Helvetica", 11)
    c.drawRightString(PAGE_WIDTH - MARGEM_DIR, y_top - 2.6 * cm, ctx["cliente"])
    c.drawRightString(PAGE_WIDTH - MARGEM_DIR, y_top - 3.4 * cm, f"Validade: {ctx['validade']}")

    y_linha = y_top - ALTURA_CABECALHO
    c.line(MARGEM_ESQ, y_linha, PAGE_WIDTH - MARGEM_DIR, y_linha)

# =====================================================
# RODAPÉ (SERÁ REESCRITO)
# =====================================================

def _rodape(c, pagina, total):
    c.setFont("Helvetica", 9)
    c.drawRightString(
        PAGE_WIDTH - MARGEM_DIR,
        MARGEM_INF + 0.7 * cm,
        f"{pagina} / {total}"
    )

    c.line(
        MARGEM_ESQ,
        MARGEM_INF + ALTURA_RODAPE - 12,
        PAGE_WIDTH - MARGEM_DIR,
        MARGEM_INF + ALTURA_RODAPE - 12,
    )

    c.setFont("Helvetica", 8)
    c.drawCentredString(
        PAGE_WIDTH / 2,
        MARGEM_INF + 4,
        "J Talent Empreendimentos | Proposta Comercial | "
        "Contato: +55 (38) 9 8422 4399 | E-mail: contato@jtalent.com.br",
    )

# =====================================================
# NOVA PÁGINA
# =====================================================

def _nova_pagina(ctx):
    # garante inicialização do buffer de páginas
    if "paginas" not in ctx:
        ctx["paginas"] = []

    ctx["paginas"].append(ctx["pagina"])  # registra página
    _rodape(ctx["c"], ctx["pagina"], 0)   # total provisório
    ctx["c"].showPage()
    ctx["pagina"] += 1
    _cabecalho_comercial(ctx)
    ctx["y"] = PAGE_HEIGHT - MARGEM_SUP - ALTURA_CABECALHO - 25

# =====================================================
# TEXTO COM QUEBRA REAL
# =====================================================

def _desenhar_texto_quebrado(ctx, texto):
    c = ctx["c"]
    linhas = texto.split("\n")

    for linha in linhas:
        p = Paragraph(linha, STYLE_TEXTO)
        w, h = p.wrap(LARGURA_UTIL, ctx["y"])

        if ctx["y"] - h < LIMITE_INFERIOR:
            _nova_pagina(ctx)

        p.drawOn(c, MARGEM_ESQ, ctx["y"] - h)
        ctx["y"] -= h

    ctx["y"] -= 10

def _desenhar_titulo(ctx, texto):
    p = Paragraph(f"<b>{texto}</b>", STYLE_TITULO)
    w, h = p.wrap(LARGURA_UTIL, ctx["y"])

    if ctx["y"] - h < LIMITE_INFERIOR:
        _nova_pagina(ctx)

    p.drawOn(ctx["c"], MARGEM_ESQ, ctx["y"] - h)
    ctx["y"] -= h + 6

def _calcular_total_paginas(
    resumo_exec,
    texto_comercial,
    valor_nf,
    cliente,
    validade,
    titulo_proposta
):
    c = canvas.Canvas(None, pagesize=A4)
    ctx = _novo_contexto(c, cliente, validade, titulo_proposta)

    _cabecalho_comercial(ctx)

    _desenhar_titulo(ctx, "Resumo Executivo")
    _desenhar_texto_quebrado(ctx, resumo_exec)

    _desenhar_titulo(ctx, "Resumo Comercial")
    _desenhar_texto_quebrado(ctx, texto_comercial)

    valor_mensal = float(valor_nf.replace("R$", "").replace(".", "").replace(",", "."))

    _desenhar_titulo(ctx, "Valores do Contrato")
    _desenhar_texto_quebrado(
        ctx,
        f"Valor mensal do contrato: R$ {valor_mensal:,.2f}\n"
        f"Valor anual do contrato (12 meses): R$ {(valor_mensal * 12):,.2f}"
    )

    return ctx["pagina"]

# =====================================================
# RELATÓRIO COMERCIAL
# =====================================================

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Frame,
    PageTemplate
)

def gerar_proposta_comercial_pdf(
    caminho,
    cliente,
    titulo_proposta,
    resumo_exec,
    _texto_inst,
    texto_comercial,
    validade,
    valor_nf,
    _margem,
    _cargos,
):
    # =====================================================
    # CONFIGURAÇÃO DO DOCUMENTO
    # =====================================================
    doc = SimpleDocTemplate(
        caminho,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=6.5 * cm,
        bottomMargin=3.5 * cm,
    )

    styles = getSampleStyleSheet()

    style_normal = ParagraphStyle(
        "TextoNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        alignment=4  # Justificado
    )

    style_titulo = ParagraphStyle(
        "TituloBloco",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        spaceAfter=12
    )

    story = []

    # =====================================================
    # CORPO DO RELATÓRIO
    # =====================================================
    story.append(Paragraph("Resumo Executivo", style_titulo))
    story.append(Paragraph(resumo_exec, style_normal))
    story.append(Spacer(1, 18))

    story.append(Paragraph("Resumo Comercial", style_titulo))
    story.append(Paragraph(texto_comercial, style_normal))
    story.append(Spacer(1, 24))

    # Valores
    valor_mensal = float(
        valor_nf.replace("R$", "").replace(".", "").replace(",", ".")
    )

    story.append(Paragraph("Valores do Contrato", style_titulo))
    story.append(
        Paragraph(
            f"""
            Valor mensal do contrato: <b>R$ {valor_mensal:,.2f}</b><br/>
            Valor anual do contrato (12 meses): 
            <b>R$ {(valor_mensal * 12):,.2f}</b>
            """,
            style_normal
        )
    )

    # =====================================================
    # CABEÇALHO E RODAPÉ
    # =====================================================
    def _desenhar_cabecalho_rodape(canvas, doc):
        largura, altura = A4

        # ---------- Cabeçalho ----------
        y_top = altura - 2.5 * cm

        # Logo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "..", "assets", "logo.png")

        if os.path.exists(logo_path):
            canvas.drawImage(
                ImageReader(logo_path),
                2.5 * cm,
                y_top - 3.5 * cm,
                width=3.2 * cm,
                height=3.2 * cm,
                preserveAspectRatio=True,
                mask="auto"
            )

        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawRightString(
            largura - 2.5 * cm,
            y_top - 0.4 * cm,
            titulo_proposta
        )

        canvas.setFont("Helvetica", 11)
        canvas.drawRightString(
            largura - 2.5 * cm,
            y_top - 1.6 * cm,
            cliente
        )

        canvas.drawRightString(
            largura - 2.5 * cm,
            y_top - 2.4 * cm,
            f"Validade: {validade}"
        )

        canvas.line(
            2.5 * cm,
            y_top - 3.2 * cm,
            largura - 2.5 * cm,
            y_top - 3.2 * cm
        )

        # ---------- Rodapé ----------
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(
            largura - 2.5 * cm,
            2.3 * cm,
            f"{canvas.getPageNumber()} / {doc.page}"
        )

        canvas.line(
            2.5 * cm,
            2.0 * cm,
            largura - 2.5 * cm,
            2.0 * cm
        )

        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(
            largura / 2,
            1.4 * cm,
            "J Talent Empreendimentos | Proposta Comercial | "
            "Contato: +55 (38) 9 8422 4399 | E-mail: contato@jtalent.com.br"
        )

    template = PageTemplate(
        id="PropostaComercial",
        frames=[
            Frame(
                doc.leftMargin,
                doc.bottomMargin,
                doc.width,
                doc.height,
                id="normal"
            )
        ],
        onFirstPage=_desenhar_cabecalho_rodape,
        onLaterPages=_desenhar_cabecalho_rodape
    )

    doc.addPageTemplates([template])
    doc.build(story)

    
# =====================================================
# RELATÓRIO TÉCNICO (VERSÃO CONGELADA)
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
    margem_sup = 3.0 * cm
    margem_inf = 3.0 * cm

    y = altura - margem_sup

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
            f"Quantidade: {cargo['Quantidade']} | "
            f"Salário Base: R$ {cargo['Salário']:,.2f}"
        )
        c.drawString(margem_esq, y, linha)
        y -= 16

        if y < margem_inf:
            c.showPage()
            y = altura - margem_sup

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(
        margem_esq,
        y,
        f"Lucro Mensal Total: R$ {lucro:,.2f}"
    )

    c.save()
