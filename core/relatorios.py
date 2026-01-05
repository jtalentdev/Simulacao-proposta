import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfgen import canvas


# =====================================================
# PARSER DE TEXTO DA IA
# =====================================================

def renderizar_texto_com_subtitulos(texto, story, style_texto, style_subtitulo):
    linhas = texto.splitlines()
    buffer = []

    def flush():
        if buffer:
            story.append(Paragraph("<br/>".join(buffer), style_texto))
            buffer.clear()

    for linha in linhas:
        linha = linha.rstrip()

        if not linha.strip():
            flush()
            continue

        if re.fullmatch(r"\*\*(.+?)\*\*", linha.strip()):
            flush()
            story.append(Paragraph(linha.strip()[2:-2], style_subtitulo))
            continue

        m = re.match(r"\*\*(.+?)\*\*[:\-]?\s*(.+)", linha)
        if m:
            flush()
            story.append(Paragraph(m.group(1), style_subtitulo))
            story.append(Paragraph(m.group(2), style_texto))
            continue

        m = re.match(r"[-•]\s*\*\*(.+?)\*\*[:\-]?\s*(.+)", linha)
        if m:
            flush()
            story.append(
                Paragraph(f"<b>- {m.group(1)}:</b> {m.group(2)}", style_texto)
            )
            continue

        m = re.match(r"(\d+\.?)\s*\*\*(.+?)\*\*[:\-]?\s*(.+)", linha)
        if m:
            flush()
            story.append(
                Paragraph(f"<b>{m.group(1)} {m.group(2)}:</b> {m.group(3)}", style_texto)
            )
            continue

        buffer.append(linha)

    flush()


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
    cargos,
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

    style_texto = ParagraphStyle("Texto", parent=styles["Normal"], fontSize=11, leading=16)
    style_titulo = ParagraphStyle("Titulo", parent=styles["Normal"], fontSize=13, fontName="Helvetica-Bold")
    style_subtitulo = ParagraphStyle("Subtitulo", parent=styles["Normal"], fontSize=12, fontName="Helvetica-Bold")

    story = []

    story.append(Paragraph("Resumo Executivo", style_titulo))
    renderizar_texto_com_subtitulos(resumo_exec, story, style_texto, style_subtitulo)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Resumo Comercial", style_titulo))
    renderizar_texto_com_subtitulos(texto_comercial, story, style_texto, style_subtitulo)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Valores do Contrato", style_titulo))

    tabela = [["Cargo", "Quantidade", "Custo unitário (R$)", "Custo total (R$)"]]

    for c in cargos:
        nome = c.get("Cargo") or c.get("cargo") or c.get("nome") or "—"
        qtd = c.get("Quantidade") or c.get("quantidade") or c.get("qtd") or 1

        custo_total = (
            c.get("Custo CLT Total (R$)")
            or c.get("custo_total")
            or c.get("custo_clt_total")
            or 0.0
        )

        custo_unit = (
            c.get("Custo CLT Unitário (R$)")
            or c.get("custo_unitario")
            or (custo_total / qtd if qtd else 0.0)
        )

        tabela.append([
            nome,
            qtd,
            f"R$ {custo_unit:,.2f}",
            f"R$ {custo_total:,.2f}",
        ])

    table = Table(tabela, colWidths=[6*cm, 3*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ]))

    story.append(table)
    story.append(Spacer(1, 18))

    valor_mensal = float(valor_nf.replace("R$", "").replace(".", "").replace(",", "."))
    story.append(Paragraph(f"<b>Valor mensal:</b> R$ {valor_mensal:,.2f}", style_texto))
    story.append(Paragraph(f"<b>Valor anual:</b> R$ {(valor_mensal*12):,.2f}", style_texto))

    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "Atenciosamente,<br/><br/>"
        "Jhonny Souza<br/>"
        "Diretor<br/>"
        "J Talent Empreendimentos<br/>"
        "+55 38 98422 4399<br/>"
        "contato@jtalent.com.br",
        style_texto
    ))

    doc.build(story)


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
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2.5 * cm, A4[1] - 3 * cm, "PROPOSTA TÉCNICA")
    c.save()
