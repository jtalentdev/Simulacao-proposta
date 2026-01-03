import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

# =====================================================
# RELATÓRIO COMERCIAL
# =====================================================

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
    c = canvas.Canvas(caminho, pagesize=A4)
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

    total_paginas = ctx["pagina"]

    # Rodapé da última página
    # registra última página
    ctx["paginas"].append(ctx["pagina"])
    
    total_paginas = len(ctx["paginas"])
    
    # reescreve rodapé corretamente em todas as páginas
    for i, pagina in enumerate(ctx["paginas"], start=1):
        ctx["c"].setPage(pagina)
        _rodape(ctx["c"], pagina, total_paginas)
    
    c.save()

    
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
