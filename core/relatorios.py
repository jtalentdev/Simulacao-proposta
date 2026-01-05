import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


# =====================================================
# UTILITÁRIO – PARSER DE TEXTO DA IA (ROBUSTO)
# =====================================================

def renderizar_texto_com_subtitulos(texto, story, style_texto, style_subtitulo):
    linhas = texto.splitlines()
    buffer_paragrafo = []

    def flush():
        if buffer_paragrafo:
            texto_par = "<br/>".join(buffer_paragrafo).strip()
            if texto_par:
                story.append(Paragraph(texto_par, style_texto))
            buffer_paragrafo.clear()

    for linha in linhas:
        linha = linha.rstrip()

        if not linha.strip():
            flush()
            continue

        # **Título**
        m = re.fullmatch(r"\*\*(.+?)\*\*", linha.strip())
        if m:
            flush()
            story.append(Paragraph(m.group(1), style_subtitulo))
            continue

        # **Título:** texto
        m = re.match(r"\*\*(.+?)\*\*[:\-]?\s*(.+)", linha)
        if m:
            flush()
            story.append(Paragraph(m.group(1), style_subtitulo))
            story.append(Paragraph(m.group(2), style_texto))
            continue

        # - **Título:** texto
        m = re.match(r"[-•]\s*\*\*(.+?)\*\*[:\-]?\s*(.+)", linha)
        if m:
            flush()
            story.append(
                Paragraph(f"<b>- {m.group(1)}:</b> {m.group(2)}", style_texto)
            )
            continue

        # 1. **Título:** texto
        m = re.match(r"(\d+\.?)\s*\*\*(.+?)\*\*[:\-]?\s*(.+)", linha)
        if m:
            flush()
            story.append(
                Paragraph(f"<b>{m.group(1)} {m.group(2)}:</b> {m.group(3)}", style_texto)
            )
            continue

        buffer_paragrafo.append(linha.strip())

    flush()


# =====================================================
# RELATÓRIO COMERCIAL (FINAL)
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
    doc = SimpleDocTemplate(
        caminho,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=7.0 * cm,
        bottomMargin=3.5 * cm,
    )

    styles = getSampleStyleSheet()

    style_texto = ParagraphStyle(
        "Texto",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=4
    )

    style_titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Normal"],
        fontSize=13,
        fontName="Helvetica-Bold",
        spaceBefore=18,
        spaceAfter=8
    )

    style_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Helvetica-Bold",
        spaceBefore=14,
        spaceAfter=6
    )

    story = []

    story.append(Paragraph("Resumo Executivo", style_titulo))
    renderizar_texto_com_subtitulos(resumo_exec, story, style_texto, style_subtitulo)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Resumo Comercial", style_titulo))
    renderizar_texto_com_subtitulos(texto_comercial, story, style_texto, style_subtitulo)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Valores do Contrato", style_titulo))

    valor_mensal = float(valor_nf.replace("R$", "").replace(".", "").replace(",", "."))
    story.append(Paragraph(
        "O valor mensal estimado para a prestação dos serviços descritos nesta proposta é de:",
        style_texto
    ))
    story.append(Paragraph(
        f"<b>R$ {valor_mensal:,.2f}</b> <font size=9>(valor mensal)</font>",
        style_texto
    ))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Considerando um período completo de 12 meses, o valor total anual do contrato será de:",
        style_texto
    ))
    story.append(Paragraph(
        f"<b>R$ {(valor_mensal * 12):,.2f}</b> <font size=9>(valor anual)</font>",
        style_texto
    ))

    def cabecalho_rodape(c, d):
        largura, altura = A4
        margem = 2.5 * cm
        topo = altura - 2.5 * cm

        logo = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        if os.path.exists(logo):
            c.drawImage(
                ImageReader(logo),
                margem,
                topo - 3.6 * cm,
                width=3.2 * cm,
                height=3.2 * cm,
                preserveAspectRatio=True,
                mask="auto"
            )

        style = ParagraphStyle("cab", fontSize=14, fontName="Helvetica-Bold", alignment=2)
        largura_texto = largura - margem * 2 - 4.6 * cm
        p = Paragraph(titulo_proposta, style)
        _, h = p.wrap(largura_texto, 4 * cm)
        p.drawOn(c, largura - margem - largura_texto, topo - 0.6 * cm - h)

        y = topo - 0.6 * cm - h - 0.4 * cm
        c.setFont("Helvetica", 11)
        c.drawRightString(largura - margem, y, cliente)
        c.drawRightString(largura - margem, y - 0.8 * cm, f"Validade: {validade}")

        c.line(margem, topo - 4.2 * cm, largura - margem, topo - 4.2 * cm)

        c.setFont("Helvetica", 8)
        c.drawCentredString(
            largura / 2,
            1.6 * cm,
            "J Talent Empreendimentos | Proposta Comercial | "
            "Contato: +55 (38) 9 8422 4399 | E-mail: contato@jtalent.com.br"
        )

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._pages = []

        def showPage(self):
            self._pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._pages)
            for p in self._pages:
                self.__dict__.update(p)
                self.setFont("Helvetica", 9)
                self.drawRightString(A4[0] - 2.5 * cm, 2.6 * cm, f"{self.getPageNumber()} / {total}")
                super().showPage()
            super().save()

    doc.build(
        story,
        onFirstPage=cabecalho_rodape,
        onLaterPages=cabecalho_rodape,
        canvasmaker=NumberedCanvas
    )


# =====================================================
# RELATÓRIO TÉCNICO (PLACEHOLDER CONGELADO)
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
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2.5 * cm, A4[1] - 3 * cm, "PROPOSTA TÉCNICA")
    c.save()
