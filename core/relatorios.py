import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


# =====================================================
# UTILITÁRIO – INTERPRETAR **SUBTÍTULOS** DA IA
# =====================================================

def renderizar_texto_com_subtitulos(texto, story, style_texto, style_subtitulo):
    blocos = texto.split("\n\n")

    for bloco in blocos:
        bloco = bloco.strip()
        if not bloco:
            continue

        # Subtítulo Markdown (**Texto**)
        if re.fullmatch(r"\*\*(.+?)\*\*", bloco):
            titulo = bloco.replace("**", "")
            story.append(Paragraph(titulo, style_subtitulo))
        else:
            story.append(Paragraph(bloco, style_texto))


# =====================================================
# RELATÓRIO COMERCIAL (PLATYPUS – DEFINITIVO)
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
    # -------------------------------------------------
    # CONFIGURAÇÃO DO DOCUMENTO
    # -------------------------------------------------
    doc = SimpleDocTemplate(
        caminho,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=7.0 * cm,      # espaço reservado ao cabeçalho
        bottomMargin=3.5 * cm,   # espaço reservado ao rodapé
    )

    styles = getSampleStyleSheet()

    # Texto normal
    style_texto = ParagraphStyle(
        "Texto",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=4  # justificado
    )

    # Título de seção
    style_titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        spaceBefore=18,
        spaceAfter=8
    )

    # Subtítulo interno (IA com **)
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

    # ==================================================
    # RESUMO EXECUTIVO
    # ==================================================
    story.append(Paragraph("Resumo Executivo", style_titulo))
    renderizar_texto_com_subtitulos(
        resumo_exec,
        story,
        style_texto,
        style_subtitulo
    )

    story.append(Spacer(1, 14))

    # ==================================================
    # RESUMO COMERCIAL
    # ==================================================
    story.append(Paragraph("Resumo Comercial", style_titulo))
    renderizar_texto_com_subtitulos(
        texto_comercial,
        story,
        style_texto,
        style_subtitulo
    )

    story.append(Spacer(1, 18))

    # ==================================================
    # VALORES DO CONTRATO
    # ==================================================
    story.append(Paragraph("Valores do Contrato", style_titulo))

    valor_mensal = float(
        valor_nf.replace("R$", "").replace(".", "").replace(",", ".")
    )

    story.append(
        Paragraph(
            "O valor mensal estimado para a prestação dos serviços descritos nesta proposta é de:",
            style_texto
        )
    )

    story.append(
        Paragraph(
            f"<b>R$ {valor_mensal:,.2f}</b> <font size=9>(valor mensal)</font>",
            style_texto
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Considerando um período completo de 12 meses, o valor total anual do contrato será de:",
            style_texto
        )
    )

    story.append(
        Paragraph(
            f"<b>R$ {(valor_mensal * 12):,.2f}</b> <font size=9>(valor anual)</font>",
            style_texto
        )
    )

    # ==================================================
    # CABEÇALHO E RODAPÉ (CONGELADOS)
    # ==================================================
    def desenhar_cabecalho_rodape(canvas_obj, doc_obj):
        largura, altura = A4
        margem_esq = 2.5 * cm
        margem_dir = 2.5 * cm
        topo = altura - 2.5 * cm

        # Logomarca
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

        # Título da proposta (com quebra automática)
        style_titulo_cab = ParagraphStyle(
            "TituloCab",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=16,
            alignment=2  # direita
        )

        largura_texto = largura - margem_dir - (margem_esq + 3.6 * cm + 1.0 * cm)
        p = Paragraph(titulo_proposta, style_titulo_cab)
        _, h = p.wrap(largura_texto, 4 * cm)
        p.drawOn(
            canvas_obj,
            largura - margem_dir - largura_texto,
            topo - 0.6 * cm - h
        )

        # Cliente e validade abaixo do título
        y_base = topo - 0.6 * cm - h - 0.4 * cm

        canvas_obj.setFont("Helvetica", 11)
        canvas_obj.drawRightString(largura - margem_dir, y_base, cliente)
        canvas_obj.drawRightString(
            largura - margem_dir,
            y_base - 0.8 * cm,
            f"Validade: {validade}"
        )

        # Linha separadora do cabeçalho
        y_linha = topo - 4.2 * cm
        canvas_obj.line(margem_esq, y_linha, largura - margem_dir, y_linha)

        # Rodapé institucional (texto)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawCentredString(
            largura / 2,
            1.6 * cm,
            "J Talent Empreendimentos | Proposta Comercial | "
            "Contato: +55 (38) 9 8422 4399 | E-mail: contato@jtalent.com.br"
        )

    # ==================================================
    # CANVAS COM NUMERAÇÃO X / Y CORRETA
    # ==================================================
    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total_paginas = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.setFont("Helvetica", 9)
                self.drawRightString(
                    A4[0] - 2.5 * cm,
                    2.6 * cm,
                    f"{self.getPageNumber()} / {total_paginas}"
                )
                super().showPage()
            super().save()

    # -------------------------------------------------
    # BUILD FINAL
    # -------------------------------------------------
    doc.build(
        story,
        onFirstPage=desenhar_cabecalho_rodape,
        onLaterPages=desenhar_cabecalho_rodape,
        canvasmaker=NumberedCanvas
    )


# =====================================================
# RELATÓRIO TÉCNICO (CONGELADO)
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
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2.5 * cm, altura - 3 * cm, "PROPOSTA TÉCNICA")
    c.save()
