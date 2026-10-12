"""Gera o PDF do relatorio da Fase 2 a partir de relatorio_mgpeb.md.

O texto fica no arquivo .md; este script so cuida da aparencia, no mesmo
padrao visual do relatorio da Fase 1. Para atualizar o PDF, edite o .md e rode:

    python3 gerar_pdf_relatorio.py

Suporta: titulo (#), secoes (##), subsecoes (###), paragrafos, listas (-),
tabelas (|), blocos de codigo (```) e imagens (![legenda](caminho)).
"""

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PASTA = Path(__file__).parent
ENTRADA_MD = PASTA / "relatorio_mgpeb.md"
SAIDA_PDF = PASTA / "relatorio_mgpeb.pdf"
LARGURA_UTIL = 17 * cm
COR_DESTAQUE = colors.HexColor("#D20A5C")
RODAPE = "Projeto Aurora Siger - Relatório Técnico do MGPEB - Fase 2"

# Fontes DejaVu: cobrem simbolos como ≥, ≤, −, ·, √ e ≈, que as fontes
# padrao do PDF nao desenham. Caem para Helvetica se nao estiverem instaladas.
PASTA_FONTES = Path("/usr/share/fonts/truetype/dejavu")
try:
    pdfmetrics.registerFont(TTFont("Texto", str(PASTA_FONTES / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("Texto-Negrito", str(PASTA_FONTES / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Texto-Italico", str(PASTA_FONTES / "DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFont(TTFont("Texto-NegritoItalico", str(PASTA_FONTES / "DejaVuSans-BoldOblique.ttf")))
    pdfmetrics.registerFont(TTFont("Mono", str(PASTA_FONTES / "DejaVuSansMono.ttf")))
    pdfmetrics.registerFontFamily(
        "Texto", normal="Texto", bold="Texto-Negrito", italic="Texto-Italico", boldItalic="Texto-NegritoItalico"
    )
    FONTE, FONTE_NEGRITO, FONTE_MONO = "Texto", "Texto-Negrito", "Mono"
except Exception:
    FONTE, FONTE_NEGRITO, FONTE_MONO = "Helvetica", "Helvetica-Bold", "Courier"

ESTILOS = {
    "titulo": ParagraphStyle("titulo", fontName=FONTE_NEGRITO, fontSize=19, leading=23,
                             textColor=colors.HexColor("#202020"), spaceAfter=8),
    "subtitulo": ParagraphStyle("subtitulo", fontName=FONTE, fontSize=9.5, leading=13,
                                textColor=colors.HexColor("#444444"), spaceAfter=2),
    "h1": ParagraphStyle("h1", fontName=FONTE_NEGRITO, fontSize=13, leading=16, textColor=COR_DESTAQUE,
                         spaceBefore=12, spaceAfter=6, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName=FONTE_NEGRITO, fontSize=10.5, leading=13,
                         textColor=colors.HexColor("#333333"), spaceBefore=6, spaceAfter=4, keepWithNext=1),
    "corpo": ParagraphStyle("corpo", fontName=FONTE, fontSize=9, leading=12.6, alignment=TA_JUSTIFY, spaceAfter=5),
    "lista": ParagraphStyle("lista", fontName=FONTE, fontSize=9, leading=12.6, leftIndent=12, bulletIndent=2,
                            spaceAfter=2),
    "celula": ParagraphStyle("celula", fontName=FONTE, fontSize=7.8, leading=9.8),
    "celula_cab": ParagraphStyle("celula_cab", fontName=FONTE_NEGRITO, fontSize=7.8, leading=9.8,
                                 textColor=colors.white),
    "codigo": ParagraphStyle("codigo", fontName=FONTE_MONO, fontSize=7.8, leading=10),
    "legenda": ParagraphStyle("legenda", fontName="Texto-Italico" if FONTE == "Texto" else "Helvetica-Oblique",
                              fontSize=8, leading=10.5, alignment=TA_CENTER,
                              textColor=colors.HexColor("#555555"), spaceBefore=3, spaceAfter=10),
}


def formatar_inline(texto):
    """Converte o Markdown de linha (negrito, italico, codigo) para as tags do reportlab."""
    texto = texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    texto = re.sub(r"`([^`]+)`", rf'<font name="{FONTE_MONO}">\1</font>', texto)
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", texto)
    texto = re.sub(r"(https?://\S+)", r'<link href="\1" color="#D20A5C">\1</link>', texto)
    return texto


def montar_tabela(linhas):
    celulas = [[c.strip() for c in linha.strip().strip("|").split("|")] for linha in linhas]
    celulas = [linha for linha in celulas if not all(re.fullmatch(r":?-{3,}:?", c) for c in linha)]
    n_colunas = len(celulas[0])

    # Largura minima de cada coluna = a maior palavra dela (nada quebra no meio da
    # palavra); o espaco que sobra e dividido conforme a quantidade de texto.
    minimos, pesos = [], []
    for col in range(n_colunas):
        textos = [linha[col] for linha in celulas if col < len(linha)]
        maior_palavra = 0
        for lin, texto in enumerate(textos):
            fonte = FONTE_NEGRITO if lin == 0 else FONTE
            for palavra in re.sub(r"[`*]", "", texto).split():
                maior_palavra = max(maior_palavra, pdfmetrics.stringWidth(palavra, fonte, 7.8))
        minimos.append(maior_palavra + 10)
        pesos.append(max(len(t) for t in textos))
    sobra = LARGURA_UTIL - sum(minimos)
    if sobra > 0:
        larguras = [m + sobra * p / sum(pesos) for m, p in zip(minimos, pesos)]
    else:
        larguras = [LARGURA_UTIL * m / sum(minimos) for m in minimos]

    dados = []
    for i, linha in enumerate(celulas):
        estilo = ESTILOS["celula_cab"] if i == 0 else ESTILOS["celula"]
        dados.append([Paragraph(formatar_inline(c), estilo) for c in linha])

    tabela = Table(dados, colWidths=larguras, repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#232323")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return [tabela, Spacer(1, 0.3 * cm)]


def montar_imagem(legenda, caminho):
    arquivo = (PASTA / caminho).resolve()
    imagem = Image(str(arquivo))
    escala = LARGURA_UTIL / imagem.imageWidth
    imagem.drawWidth = LARGURA_UTIL
    imagem.drawHeight = imagem.imageHeight * escala
    return [KeepTogether([imagem, Paragraph(formatar_inline(legenda), ESTILOS["legenda"])])]


def converter_markdown(texto):
    story = []
    linhas = texto.splitlines()
    i = 0
    antes_da_primeira_secao = True

    while i < len(linhas):
        linha = linhas[i]

        if not linha.strip():
            i += 1
            continue

        if linha.startswith("```"):
            bloco = []
            i += 1
            while i < len(linhas) and not linhas[i].startswith("```"):
                bloco.append(linhas[i])
                i += 1
            i += 1
            caixa = Table([[Preformatted("\n".join(bloco), ESTILOS["codigo"])]], colWidths=[LARGURA_UTIL])
            caixa.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F2F2")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.extend([Spacer(1, 0.1 * cm), caixa, Spacer(1, 0.3 * cm)])
            continue

        if linha.startswith("|"):
            bloco = []
            while i < len(linhas) and linhas[i].startswith("|"):
                bloco.append(linhas[i])
                i += 1
            story.extend(montar_tabela(bloco))
            continue

        imagem = re.fullmatch(r"!\[(.*)\]\((.+)\)", linha.strip())
        if imagem:
            story.extend(montar_imagem(imagem.group(1), imagem.group(2)))
            i += 1
            continue

        if linha.startswith("# "):
            story.append(Paragraph(formatar_inline(linha[2:]), ESTILOS["titulo"]))
            i += 1
            continue

        if linha.startswith("## "):
            antes_da_primeira_secao = False
            story.append(Paragraph(formatar_inline(linha[3:]), ESTILOS["h1"]))
            i += 1
            continue

        if linha.startswith("### "):
            story.append(Paragraph(formatar_inline(linha[4:]), ESTILOS["h2"]))
            i += 1
            continue

        if linha.startswith("- "):
            while i < len(linhas) and linhas[i].startswith("- "):
                story.append(Paragraph(formatar_inline(linhas[i][2:]), ESTILOS["lista"], bulletText="•"))
                i += 1
            story.append(Spacer(1, 0.15 * cm))
            continue

        # Paragrafo comum: junta as linhas ate a proxima linha em branco.
        paragrafo = []
        while i < len(linhas) and linhas[i].strip() and not re.match(r"(#|\||```|- |!\[)", linhas[i]):
            paragrafo.append(linhas[i].strip())
            i += 1
        estilo = ESTILOS["subtitulo"] if antes_da_primeira_secao else ESTILOS["corpo"]
        story.append(Paragraph(formatar_inline(" ".join(paragrafo)), estilo))

    return story


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONTE, 7.5)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(2 * cm, 1.2 * cm, RODAPE)
    canvas.drawRightString(19 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def gerar_pdf():
    doc = SimpleDocTemplate(
        str(SAIDA_PDF),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Relatório Técnico - MGPEB - Aurora Siger",
        author="Grupo 42",
    )
    story = converter_markdown(ENTRADA_MD.read_text(encoding="utf-8"))
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print(f"PDF gerado em {SAIDA_PDF}")


if __name__ == "__main__":
    gerar_pdf()
