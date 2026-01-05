import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


# =====================================================
# UTILITÁRIO – INTERPRETAR TEXTO DA IA (ROBUSTO E FIEL)
# =====================================================

def renderizar_texto_com_subtitulos(texto, story, style_texto, style_subtitulo):
    linhas = texto.splitlines()
    buffer_paragrafo = []

    def flush_paragrafo():
        if buffer_paragrafo:
            texto_par = "<br/>".join(buffer_paragrafo).strip()
            if texto_par:
                story.append(Paragraph(texto_par, style_texto))
            buffer_paragrafo.clear()

    for linha in linhas:
        linha = linha.rstrip()

        # Linha vazia = quebra de parágrafo
        if not linha.strip():
            flush_paragrafo()
            continue

        # 1) **Título**
        match_titulo = re.fullmatch(r"\*\*(.+?)\*\*", linha.strip())
        if match_titulo:
            flush_paragrafo()
            story.append(Paragraph(match_titulo.group(1), style_subtitulo))
            continue

        # 2) **Título:** texto
        match_inline = re.match(r"\*\*(.+?)\*\*[:\-]?\s*(.+)", linha)
        if match_inline:
            flush_paragrafo()
            story.append(Paragraph(match_inline.group(1), style_subtitulo))
            story.append(Paragraph(match_inline.group(2), style_texto))
            continue

        # 3) - **Título:** texto
        match_bullet = re.match(r"[-•]\s*\*\*(.+?)\*\*[:\-]?\s*(.+)", linha)
        if match_bullet:
            flush_paragrafo()
            story.append(
                Paragraph(
                    f"<b>- {match_bullet.group(1)}:</b> {match_bullet.group(2)}",
                    style_texto
                )
            )
            continue

        # 4) 1. **Título:** texto
        match_num = re.match(r"(\d+\.?)\s*\*\*(.+?)\*\*[:\-]?\s*(.+)", linha)
        if match_num:
            flush_paragrafo()
            story.append(
                Paragraph(
                    f"<b>{match_num.group(1)} {match_num.group(2)}:</b> {match_num.group(3)}",
                    style_texto
                )
            )
            continue

        # 5) Texto normal (mantém ENTER como <br/>)
        buffer_paragrafo.append(linha.strip())

    flush_paragrafo()


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
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=7.0 * cm,
        bottomMargin=3.5 * cm,
    )

    styles = getSampleStyleSheet()

    style_texto = ParagraphStyle(
        "Texto",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=4
    )

    style_titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        spaceBefore=18,
        spaceAfter=8
    )

    style_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
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

    # Cabeçalho, rodapé e numeração permanecem CONGELADOS
    def desenhar_cabecalho_rodape(canvas_obj, doc_obj):
        largura, altura = A4
        margem_esq, margem_dir = 2.5 * cm, 2.5 * cm
        topo = altura - 2.5 * cm

        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "..", "assets", "logo.png")

        if os.path.exists(logo_path):
            canvas_obj.drawImage(
                ImageReader(logo_path),
                margem_esq,
                topo - 3.6 * cm,
                width=3.2 * cm,
                height=3.2 * cm,
                preserveAspectRatio=True,
                mask="auto"
            )

        style_cab = ParagraphStyle("Cab", fontName="Helvetica-Bold", fontSize=14, alignment=2)
        largura_texto = largura - margem_dir - (margem_esq + 3.6 * cm + 1 * cm)
        p = Paragraph(titulo_proposta, style_cab)
        _, h = p.wrap(largura_texto, 4 * cm)
        p.drawOn(canvas_obj, largura - margem_dir - largura_texto, topo - 0.6 * cm - h)

        y = topo - 0.6 * cm - h - 0.4 * cm
        canvas_obj.setFont("Helvetica", 11)
        canvas_obj.drawRightString(largura - margem_dir, y, cliente)
        canvas_obj.drawRightString(largura - margem_dir, y - 0.8 * cm, f"Validade: {validade}")

        canvas_obj.line(margem_esq, topo - 4.2 * cm, largura - margem_dir, topo - 4.2 * cm)

        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawCentredString(
            largura / 2, 1.6 * cm,
            "J Talent Empreendimentos | Proposta Comercial | "
            "Contato: +55 (38) 9 8422 4399 | E-mail: contato@jtalent.com.br"
        )

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.setFont("Helvetica", 9)
                self.drawRightString(A4[0] - 2.5 * cm, 2.6 * cm, f"{self.getPageNumber()} / {total}")
                super().showPage()
            super().save()

    doc.build(
        story,
        onFirstPage=desenhar_cabecalho_rodape,
        onLaterPages=desenhar_cabecalho_rodape,
        canvasmaker=NumberedCanvas
    )
