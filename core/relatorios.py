import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawRightString(
            A4[0] - 2.5 * cm,
            2.6 * cm,
            f"{self.getPageNumber()} / {page_count}"
        )


# =====================================================
# RELATÓRIO COMERCIAL (PLATYPUS - DEFINITIVO)
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

    style_texto = ParagraphStyle(
        "Texto",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        alignment=4  # justificado
    )

    style_titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        spaceAfter=10
    )

    story = []

    # -------------------------------------------------
    # CORPO DO RELATÓRIO
    # -------------------------------------------------
    story.append(Paragraph("Resumo Executivo", style_titulo))
    story.append(Paragraph(resumo_exec, style_texto))
    story.append(Spacer(1, 18))

    story.append(Paragraph("Resumo Comercial", style_titulo))
    story.append(Paragraph(texto_comercial, style_texto))
    story.append(Spacer(1, 24))

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
            style_texto
        )
    )

    # -------------------------------------------------
    # CABEÇALHO E RODAPÉ (TODAS AS PÁGINAS)
    # -------------------------------------------------
    def desenhar_cabecalho_rodape(canvas, doc):
        largura, altura = A4

        margem_esq = 2.5 * cm
        margem_dir = 2.5 * cm
        topo = altura - 2.5 * cm

        # -------- LOGOMARCA --------
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "..", "assets", "logo.png")

        if os.path.exists(logo_path):
            canvas.drawImage(
                ImageReader(logo_path),
                margem_esq,
                topo - 3.6 * cm,
                width=3.2 * cm,
                height=3.2 * cm,
                preserveAspectRatio=True,
                mask="auto"
            )

        # -------- TEXTO À DIREITA --------
        style_titulo_cab = ParagraphStyle(
            "TituloCabecalho",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=16,
            alignment=2  # alinhado à direita
        )
        
        p = Paragraph(titulo_proposta, style_titulo_cab)
        
        # largura disponível (não invade a logo)
        largura_texto = largura - margem_dir - (margem_esq + 3.6 * cm + 1.0 * cm)
        
        w, h = p.wrap(largura_texto, 4 * cm)
        
        p.drawOn(
            canvas,
            largura - margem_dir - largura_texto,
            topo - 0.6 * cm - h
        )


        # posição base abaixo do título
        y_base = topo - 0.6 * cm - h - 0.4 * cm
        
        canvas.setFont("Helvetica", 11)
        canvas.drawRightString(
            largura - margem_dir,
            y_base,
            cliente
        )
        
        canvas.drawRightString(
            largura - margem_dir,
            y_base - 0.8 * cm,
            f"Validade: {validade}"
        )


        # -------- LINHA DO CABEÇALHO --------
        y_linha = topo - 4.2 * cm
        canvas.line(
            margem_esq,
            y_linha,
            largura - margem_dir,
            y_linha
        )

        # -------- RODAPÉ --------
        canvas.setFont("Helvetica", 9)
        
        canvas.line(
            margem_esq,
            2.3 * cm,
            largura - margem_dir,
            2.3 * cm
        )

        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(
            largura / 2,
            1.6 * cm,
            "J Talent Empreendimentos | Proposta Comercial | "
            "Contato: +55 (38) 9 8422 4399 | E-mail: contato@jtalent.com.br"
        )

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
# RELATÓRIO TÉCNICO (MANTIDO CONGELADO)
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

    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2.5 * cm, altura - 3 * cm, "PROPOSTA TÉCNICA")

    c.save()
