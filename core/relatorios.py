import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader

# =====================================================
# CONFIGURAÇÕES GERAIS
# =====================================================

MARGEM_ESQ = 2.5 * cm
MARGEM_DIR = 2.5 * cm
MARGEM_INF = 3.0 * cm
LARGURA_TEXTO = A4[0] - (MARGEM_ESQ + MARGEM_DIR)

FONT_TEXTO = "Helvetica"
FONT_TITULO = "Helvetica-Bold"

SIZE_TEXTO = 11
SIZE_TITULO = 14
SIZE_TITULO_GRANDE = 16

LEADING = 16
ESPACO_PARAGRAFO = 6

# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================

def _footer(c, pagina):
    c.setFont("Helvetica-Oblique", 8)
    c.drawRightString(
        A4[0] - MARGEM_DIR,
        1.5 * cm,
        f"Página {pagina}"
    )


def _nova_pagina(c, pagina, titulo, subtitulo):
    _footer(c, pagina)
    c.showPage()
    pagina += 1
    y = _cabecalho(c, titulo, subtitulo)
    return y, pagina


def _cabecalho(c, titulo, subtitulo):
    largura, altura = A4

    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "..", "assets", "logo.png")

    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(
            logo,
            MARGEM_ESQ,
            altura - 4.5 * cm,
            width=3.5 * cm,
            height=3.5 * cm,
            preserveAspectRatio=True,
            mask="auto"
        )

    y = altura - 2.5 * cm

    c.setFont(FONT_TITULO, SIZE_TITULO_GRANDE)
    c.drawRightString(
        A4[0] - MARGEM_DIR,
        y,
        titulo
    )
    y -= 18

    c.setFont(FONT_TEXTO, 11)

    palavras = subtitulo.split()
    linha = ""

    for p in palavras:
        teste = linha + p + " "
        if stringWidth(teste, FONT_TEXTO, 11) <= (A4[0] - MARGEM_DIR - MARGEM_ESQ - 4.5 * cm):
            linha = teste
        else:
            c.drawRightString(A4[0] - MARGEM_DIR, y, linha.strip())
            y -= 14
            linha = p + " "

    if linha:
        c.drawRightString(A4[0] - MARGEM_DIR, y, linha.strip())

    return y - 20


def _draw_linha_justificada(c, palavras, y):
    largura_palavras = sum(
        stringWidth(p, FONT_TEXTO, SIZE_TEXTO) for p in palavras
    )
    espaco = (LARGURA_TEXTO - largura_palavras) / (len(palavras) - 1)
    x = MARGEM_ESQ

    for p in palavras:
        c.drawString(x, y, p)
        x += stringWidth(p, FONT_TEXTO, SIZE_TEXTO) + espaco


def _draw_texto(c, texto, y, pagina, titulo, subtitulo):
    c.setFont(FONT_TEXTO, SIZE_TEXTO)

    for linha_raw in texto.split("\n"):
        linha_raw = linha_raw.strip()

        if not linha_raw:
            y -= ESPACO_PARAGRAFO
            continue

        # TÍTULO (REGRA A)
        if linha_raw.startswith("**") and linha_raw.endswith("**"):
            titulo_txt = linha_raw.replace("**", "").strip()

            if y < MARGEM_INF:
                y, pagina = _nova_pagina(c, pagina, titulo, subtitulo)

            c.setFont(FONT_TITULO, SIZE_TITULO)

            palavras = titulo_txt.split()
            linha = ""

            for p in palavras:
                teste = linha + p + " "
                if stringWidth(teste, FONT_TITULO, SIZE_TITULO) <= LARGURA_TEXTO:
                    linha = teste
                else:
                    c.drawString(MARGEM_ESQ, y, linha.strip())
                    y -= LEADING
                    linha = p + " "

            if linha:
                c.drawString(MARGEM_ESQ, y, linha.strip())
                y -= LEADING

            c.setFont(FONT_TEXTO, SIZE_TEXTO)
            continue

        palavras = linha_raw.split()
        linha = []
        largura = 0

        for p in palavras:
            w = stringWidth(p + " ", FONT_TEXTO, SIZE_TEXTO)
            if largura + w <= LARGURA_TEXTO:
                linha.append(p)
                largura += w
            else:
                if y < MARGEM_INF:
                    y, pagina = _nova_pagina(c, pagina, titulo, subtitulo)
                _draw_linha_justificada(c, linha, y)
                y -= LEADING
                linha = [p]
                largura = w

        if linha:
            if y < MARGEM_INF:
                y, pagina = _nova_pagina(c, pagina, titulo, subtitulo)
            c.drawString(MARGEM_ESQ, y, " ".join(linha))
            y -= LEADING

        y -= ESPACO_PARAGRAFO

    return y, pagina

# =====================================================
# PROPOSTA COMERCIAL
# =====================================================

def gerar_proposta_comercial_pdf(
    caminho,
    cliente,
    titulo_proposta,
    resumo,
    texto_inst,
    texto_comercial,
    validade,
    valor_nf,
    margem,
    cargos
):
    c = canvas.Canvas(caminho, pagesize=A4)
    pagina = 1

    y = _cabecalho(
        c,
        "PROPOSTA COMERCIAL",
        f"{cliente} | Validade: {validade}"
    )

    y, pagina = _draw_texto(
        c,
        f"**{titulo_proposta}**",
        y,
        pagina,
        "PROPOSTA COMERCIAL",
        cliente
    )

    y, pagina = _draw_texto(
        c,
        resumo,
        y,
        pagina,
        "PROPOSTA COMERCIAL",
        cliente
    )

    c.setFont(FONT_TITULO, 18)
    c.drawString(MARGEM_ESQ, y, valor_nf)

    y, pagina = _nova_pagina(c, pagina, "PROPOSTA COMERCIAL", cliente)

    if texto_inst:
        y, pagina = _draw_texto(
            c,
            texto_inst,
            y,
            pagina,
            "PROPOSTA COMERCIAL",
            cliente
        )

    y, pagina = _draw_texto(
        c,
        texto_comercial,
        y,
        pagina,
        "PROPOSTA COMERCIAL",
        cliente
    )

    assinatura = (
        "Atenciosamente,\n\n"
        "Jhonny Souza\n"
        "J Talent – Equipe Comercial\n"
        "Telefone: +55 38 98422 4399\n"
        "E-mail: contato@jtalent.com.br"
    )

    y, pagina = _draw_texto(
        c,
        assinatura,
        y,
        pagina,
        "PROPOSTA COMERCIAL",
        cliente
    )

    _footer(c, pagina)
    c.save()

# =====================================================
# PROPOSTA TÉCNICA
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
    pagina = 1

    y = _cabecalho(
        c,
        "PROPOSTA TÉCNICA",
        "Memória de Cálculo – Custos, Encargos e Tributos"
    )

    y, pagina = _draw_texto(
        c,
        "**Custos por Cargo**",
        y,
        pagina,
        "PROPOSTA TÉCNICA",
        "Memória de Cálculo – Custos, Encargos e Tributos"
    )

    for cargo in cargos:
        linha = (
            f"{cargo['Cargo']} | "
            f"Qtd: {cargo['Quantidade']} | "
            f"Salário Base: R$ {cargo['Salário']:,.2f}"
        )
        y, pagina = _draw_texto(
            c,
            linha,
            y,
            pagina,
            "PROPOSTA TÉCNICA",
            "Memória de Cálculo – Custos, Encargos e Tributos"
        )

    y, pagina = _draw_texto(
        c,
        f"**Lucro Mensal: R$ {lucro:,.2f}**",
        y,
        pagina,
        "PROPOSTA TÉCNICA",
        "Memória de Cálculo – Custos, Encargos e Tributos"
    )

    _footer(c, pagina)
    c.save()
