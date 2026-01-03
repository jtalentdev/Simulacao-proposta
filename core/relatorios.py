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

def _cabecalho_comercial(c, cliente, validade):
    largura, altura = A4

    margem_esq = 2.5 * cm
    margem_dir = 2.5 * cm
    margem_top = 2.5 * cm

    altura_cabecalho = 4.0 * cm
    y_topo = altura - margem_top

    # Logo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "..", "assets", "logo.png")

    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(
            logo,
            margem_esq,
            y_topo - altura_cabecalho + 0.5 * cm,
            width=3.2 * cm,
            height=3.2 * cm,
            preserveAspectRatio=True,
            mask="auto"
        )

    # Texto à direita
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(largura - margem_dir, y_topo - 0.5 * cm, "PROPOSTA COMERCIAL")

    c.setFont("Helvetica", 11)
    c.drawRightString(largura - margem_dir, y_topo - 1.6 * cm, cliente)

    c.drawRightString(
        largura - margem_dir,
        y_topo - 2.6 * cm,
        f"Validade: {validade}"
    )

    # Linha horizontal
    y_linha = y_topo - altura_cabecalho
    c.line(margem_esq, y_linha, largura - margem_dir, y_linha)

    # Retorna Y inicial do corpo (2 espaçamentos abaixo)
    return y_linha - (2 * 14)

def _rodape_comercial(c, pagina_atual, total_paginas):
    largura, _ = A4
    margem_dir = 2.5 * cm
    margem_inf = 2.0 * cm

    # Numeração
    c.setFont("Helvetica", 9)
    c.drawRightString(
        largura - margem_dir,
        margem_inf + 0.6 * cm,
        f"{pagina_atual} / {total_paginas}"
    )

    # Linha
    c.line(
        margem_dir,
        margem_inf,
        largura - margem_dir,
        margem_inf
    )

    # Texto centralizado
    c.setFont("Helvetica", 8)
    c.drawCentredString(
        largura / 2,
        margem_inf - 0.6 * cm,
        "J Talent Empreendimentos | Proposta Comercial | "
        "Contato: +55 (38) 9 8422 4399 | E-mail: contato@jtalent.com.br"
    )

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
    resumo_exec,
    _texto_inst,
    texto_comercial,
    validade,
    valor_mensal,
    _margem,
    _cargos
):
    c = canvas.Canvas(caminho, pagesize=A4)

    paginas = []
    largura, altura = A4
    margem_esq = 2.5 * cm
    margem_dir = 2.5 * cm
    margem_inf = 3.0 * cm

    # Página 1
    y = _cabecalho_comercial(c, cliente, validade)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem_esq, y, "Resumo Executivo")
    y -= 18

    c.setFont("Helvetica", 11)
    y = _draw_texto(c, resumo_exec, y, 1, "", "")[0]

    y -= 12
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem_esq, y, "Resumo Comercial")
    y -= 18

    c.setFont("Helvetica", 11)
    y = _draw_texto(c, texto_comercial, y, 1, "", "")[0]

    # Valores
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem_esq, y, "Valor do Contrato")
    y -= 18

    valor_mensal_float = float(
        valor_mensal.replace("R$", "").replace(".", "").replace(",", ".")
    )

    c.setFont("Helvetica", 11)
    c.drawString(
        margem_esq,
        y,
        f"Valor mensal: R$ {valor_mensal_float:,.2f}"
    )
    y -= 16

    c.drawString(
        margem_esq,
        y,
        f"Valor anual (12 meses): R$ {(valor_mensal_float * 12):,.2f}"
    )

    paginas.append(c.getPageNumber())
    total_paginas = len(paginas)

    _rodape_comercial(c, 1, total_paginas)
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
