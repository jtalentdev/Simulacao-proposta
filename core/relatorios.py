import os
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
MARGEM_INF = 2.5 * cm

ALTURA_CABECALHO = 4.0 * cm
ALTURA_RODAPE = 2.0 * cm

LIMITE_INFERIOR_UTIL = MARGEM_INF + ALTURA_RODAPE + 10
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
        "y": PAGE_HEIGHT - MARGEM_SUP - ALTURA_CABECALHO - 30,
        "cliente": cliente,
        "validade": validade,
        "titulo": titulo,
    }

# =====================================================
# CABEÇALHO
# =====================================================

def _cabecalho_comercial(ctx):
    c = ctx["c"]
    y_top = PAGE_HEIGHT - MARGEM_SUP

    # Logo
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

    # Título da proposta (quebra controlada)
    p = Paragraph(ctx["titulo"], STYLE_CABECALHO)
    w, h = p.wrap(LARGURA_UTIL - 4 * cm, ALTURA_CABECALHO)
    p.drawOn(
        c,
        PAGE_WIDTH - MARGEM_DIR - w,
        y_top - 0.8 * cm - h
    )

    c.setFont("Helvetica", 11)
    c.drawRightString(
        PAGE_WIDTH - MARGEM_DIR,
        y_top - 2.6 * cm,
        ctx["cliente"]
    )

    c.drawRightString(
        PAGE_WIDTH - MARGEM_DIR,
        y_top - 3.4 * cm,
        f"Validade: {ctx['validade']}"
    )

    y_linha = y_top - ALTURA_CABECALHO
    c.line(MARGEM_ESQ, y_linha, PAGE_WIDTH - MARGEM_DIR, y_linha)

# =====================================================
# RODAPÉ
# =====================================================

def _rodape_comercial(ctx, total_paginas):
    c = ctx["c"]

    c.setFont("Helvetica", 9)
    c.drawRightString(
        PAGE_WIDTH - MARGEM_DIR,
        MARGEM_INF + 0.6 * cm,
        f"Página {ctx['pagina']} / {total_paginas}"
    )

    c.line(
        MARGEM_ESQ,
        MARGEM_INF + ALTURA_RODAPE - 10,
        PAGE_WIDTH - MARGEM_DIR,
        MARGEM_INF + ALTURA_RODAPE - 10,
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
    _rodape_comercial(ctx, 0)
    ctx["c"].showPage()
    ctx["pagina"] += 1
    _cabecalho_comercial(ctx)
    ctx["y"] = PAGE_HEIGHT - MARGEM_SUP - ALTURA_CABECALHO - 30

# =====================================================
# DESENHO
# =====================================================

def _desenhar_titulo(ctx, texto):
    p = Paragraph(f"<b>{texto}</b>", STYLE_TITULO)
    w, h = p.wrap(LARGURA_UTIL, ctx["y"])

    if ctx["y"] - h < LIMITE_INFERIOR_UTIL:
        _nova_pagina(ctx)

    p.drawOn(ctx["c"], MARGEM_ESQ, ctx["y"] - h)
    ctx["y"] -= h + 6


def _desenhar_bloco(ctx, texto):
    p = Paragraph(texto.replace("\n", "<br/>"), STYLE_TEXTO)
    w, h = p.wrap(LARGURA_UTIL, ctx["y"])

    if ctx["y"] - h < LIMITE_INFERIOR_UTIL:
        _nova_pagina(ctx)

    p.drawOn(ctx["c"], MARGEM_ESQ, ctx["y"] - h)
    ctx["y"] -= h + 10

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
    _desenhar_bloco(ctx, resumo_exec)

    _desenhar_titulo(ctx, "Resumo Comercial")
    _desenhar_bloco(ctx, texto_comercial)

    # Valores corretos
    valor_mensal = float(
        valor_nf.replace("R$", "").replace(".", "").replace(",", ".")
    )

    _desenhar_titulo(ctx, "Valores do Contrato")
    _desenhar_bloco(
        ctx,
        f"Valor mensal do contrato: <b>R$ {valor_mensal:,.2f}</b><br/>"
        f"Valor anual do contrato (12 meses): "
        f"<b>R$ {(valor_mensal * 12):,.2f}</b>"
    )

    total_paginas = ctx["pagina"]
    _rodape_comercial(ctx, total_paginas)
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
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm

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
