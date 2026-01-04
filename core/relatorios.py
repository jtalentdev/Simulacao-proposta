import os
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Frame,
    PageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader


# =====================================================
# RELATÓRIO COMERCIAL – VERSÃO RECONSTRUÍDA
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
        topMargin=6.8 * cm,      # espaço reservado para cabeçalho
        bottomMargin=3.2 * cm,   # espaço reservado para rodapé
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
    # CABEÇALHO E RODAPÉ
    # -------------------------------------------------
    def desenhar_cabecalho_rodape(canvas, doc):
        largura, altura = A4

        margem_esq = 2.5 * cm
        margem_dir = 2.5 * cm
        topo = altura - 2.5 * cm

        # -------- LOGO --------
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "..", "assets", "logo.png")

        if os.path.exists(logo_path):
            canvas.drawImage(
                ImageReader(logo_path),
                margem_esq,
                topo - 3.8 * cm,
                width=3.2 * cm,
                height=3.2 * cm,
                preserveAspectRatio=True,
                mask="auto"
            )

        # -------- TEXTO À DIREITA --------
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawRightString(
            largura - margem_dir,
            topo - 0.6 * cm,
            titulo_proposta
        )

        canvas.setFont("Helvetica", 11)
        canvas.drawRightString(
            largura - margem_dir,
            topo - 1.8 * cm,
            cliente
        )

        canvas.drawRightString(
            largura - margem_dir,
            topo - 2.6 * cm,
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
        canvas.drawRightString(
            largura - margem_dir,
            2.4 * cm,
            f"{canvas.getPageNumber()} / {doc.page}"
        )

        canvas.line(
            margem_esq,
            2.1 * cm,
            largura - margem_dir,
            2.1 * cm
        )

        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(
            largura / 2,
            1.5 * cm,
            "J Talent Empreendimentos | Proposta Comercial | "
            "Contato: +55 (38) 9 8422 4399 | E-mail: contato@jtalent.com.br"
        )

    # -------------------------------------------------
    # TEMPLATE DE PÁGINA
    # -------------------------------------------------
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="corpo"
    )

    template = PageTemplate(
        id="PropostaComercial",
        frames=[frame],
        onPage=desenhar_cabecalho_rodape
    )

    doc.addPageTemplates([template])
    doc.build(story)


# =====================================================
# RELATÓRIO TÉCNICO (MANTIDO CONGELADO / SIMPLES)
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
