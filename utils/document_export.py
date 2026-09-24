from io import BytesIO
import html
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Mm, Inches
from docx.enum.table import WD_TABLE_ALIGNMENT

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib import colors


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"


# ---------------------------------------------------------
# Text Sanitization
# ---------------------------------------------------------

def sanitize_text(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
        "",
        text,
    )

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------
# Terms Extraction
# ---------------------------------------------------------

def extract_terms(text: str) -> list[str]:
    """
    Extract terms from semicolon-separated input or
    bullet-style terms contained in generated text.
    """

    cleaned = sanitize_text(text)

    if not cleaned:
        return []

    terms = []

    # First look for bullet-style lines.
    for line in cleaned.splitlines():
        line = line.strip()

        bullet_match = re.match(
            r"^[-•*]\s+(.+)",
            line,
        )

        if bullet_match:
            value = bullet_match.group(1).strip()

            if value:
                terms.append(value)

    # If no bullets exist, look for semicolon-separated
    # content.
    if not terms:
        for line in cleaned.splitlines():
            if ";" in line:
                parts = [
                    part.strip()
                    for part in line.split(";")
                    if part.strip()
                ]

                if len(parts) > 1:
                    terms.extend(parts)

    # Remove duplicates while preserving order.
    unique_terms = []

    for term in terms:
        if term not in unique_terms:
            unique_terms.append(term)

    return unique_terms


# ---------------------------------------------------------
# HTML Preview
# ---------------------------------------------------------

def format_html_preview(text: str) -> str:
    text = sanitize_text(text)

    if not text:
        return """
        <div class="legal-empty">
            No document content available.
        </div>
        """

    html_blocks = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            html_blocks.append(
                '<div class="legal-spacer"></div>'
            )
            continue

        escaped_line = html.escape(line)

        numbered_heading = re.match(
            r"^\d+\.\s+.+",
            line,
        )

        upper_heading = (
            len(line) <= 100
            and line.upper() == line
            and any(char.isalpha() for char in line)
        )

        bullet_line = re.match(
            r"^[-•*]\s+(.+)",
            line,
        )

        if numbered_heading or upper_heading:
            html_blocks.append(
                f'<div class="legal-heading">{escaped_line}</div>'
            )

        elif bullet_line:
            bullet_text = html.escape(
                bullet_line.group(1)
            )

            html_blocks.append(
                f'<div class="legal-bullet">• {bullet_text}</div>'
            )

        else:
            html_blocks.append(
                f'<div class="legal-paragraph">{escaped_line}</div>'
            )

    content = "\n".join(html_blocks)

    return f"""
<style>
.legal-preview-card {{
    background-color: #151515;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 30px;
    height: 650px;
    overflow-y: auto;
    color: #eeeeee;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 16px;
    line-height: 1.7;
    box-sizing: border-box;
}}

.legal-preview-title {{
    color: #ffffff;
    font-family: Arial, sans-serif;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 18px;
}}

.legal-heading {{
    color: #ffffff;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 17px;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 8px;
}}

.legal-paragraph {{
    margin-bottom: 10px;
}}

.legal-bullet {{
    margin-left: 20px;
    margin-bottom: 7px;
}}

.legal-spacer {{
    height: 8px;
}}

.legal-empty {{
    padding: 20px;
    color: #888888;
}}
</style>

<div class="legal-preview-title">
    ⚖️ LegalEase Document Preview
</div>

<div class="legal-preview-card">
    {content}
</div>
"""


# ---------------------------------------------------------
# TXT Export
# ---------------------------------------------------------

def create_txt(document_text: str) -> bytes:
    cleaned_text = sanitize_text(document_text)

    return cleaned_text.encode("utf-8")


# ---------------------------------------------------------
# DOCX Export
# ---------------------------------------------------------

def create_docx(document_text: str) -> bytes:
    document_text = sanitize_text(document_text)

    document = Document()

    section = document.sections[0]

    section.top_margin = Mm(20)
    section.bottom_margin = Mm(20)
    section.left_margin = Mm(20)
    section.right_margin = Mm(20)

    # Logo
    if LOGO_PATH.exists():
        logo_paragraph = document.add_paragraph()
        logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = logo_paragraph.add_run()
        run.add_picture(
            str(LOGO_PATH),
            width=Inches(2.4),
        )

    # Title
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = title.add_run("LEGALEASE")
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(18)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = subtitle.add_run(
        "AI-Powered Legal Document"
    )

    run.font.name = "Times New Roman"
    run.font.size = Pt(11)

    document.add_paragraph()

    # Main document
    for line in document_text.splitlines():
        line = line.strip()

        if not line:
            document.add_paragraph()
            continue

        paragraph = document.add_paragraph()

        is_heading = (
            bool(re.match(r"^\d+\.\s+.+", line))
            or (
                len(line) <= 100
                and line.upper() == line
                and any(char.isalpha() for char in line)
            )
        )

        bullet_match = re.match(
            r"^[-•*]\s+(.+)",
            line,
        )

        if is_heading:
            run = paragraph.add_run(line)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        elif bullet_match:
            run = paragraph.add_run(
                "• " + bullet_match.group(1)
            )
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        else:
            run = paragraph.add_run(line)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

    # Terms table
    terms = extract_terms(document_text)

    if terms:
        document.add_paragraph()

        terms_heading = document.add_paragraph()

        run = terms_heading.add_run(
            "KEY TERMS AND CONDITIONS"
        )

        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)

        table = document.add_table(
            rows=1,
            cols=2,
        )

        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"

        header_cells = table.rows[0].cells

        header_cells[0].text = "No."
        header_cells[1].text = "Term / Condition"

        for index, term in enumerate(terms, start=1):
            cells = table.add_row().cells

            cells[0].text = str(index)
            cells[1].text = term

        document.add_paragraph()

    # AI notice
    notice = document.add_paragraph()
    notice.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = notice.add_run(
        "AI-generated draft. Review by a qualified "
        "legal professional before signing or relying "
        "upon this document."
    )

    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)

    output = BytesIO()

    document.save(output)

    return output.getvalue()


# ---------------------------------------------------------
# PDF Export
# ---------------------------------------------------------

def create_pdf(document_text: str) -> bytes:
    document_text = sanitize_text(document_text)

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "LegalEaseTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "LegalEaseSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    heading_style = ParagraphStyle(
        "LegalEaseHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        spaceBefore=8,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "LegalEaseBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "LegalEaseBullet",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-8,
        spaceAfter=5,
    )

    notice_style = ParagraphStyle(
        "LegalEaseNotice",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        spaceBefore=12,
    )

    story = []

    # Logo
    if LOGO_PATH.exists():
        logo = Image(
            str(LOGO_PATH),
            width=55 * mm,
            height=55 * mm,
        )

        logo.hAlign = "CENTER"

        story.append(logo)
        story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "LEGALEASE",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "AI-Powered Legal Document",
            subtitle_style,
        )
    )

    story.append(
        Spacer(1, 8)
    )

    # Main document
    for line in document_text.splitlines():
        line = line.strip()

        if not line:
            story.append(
                Spacer(1, 5)
            )
            continue

        safe_line = html.escape(line)

        is_heading = (
            bool(re.match(r"^\d+\.\s+.+", line))
            or (
                len(line) <= 100
                and line.upper() == line
                and any(char.isalpha() for char in line)
            )
        )

        bullet_match = re.match(
            r"^[-•*]\s+(.+)",
            line,
        )

        if is_heading:
            story.append(
                Paragraph(
                    safe_line,
                    heading_style,
                )
            )

        elif bullet_match:
            bullet_text = html.escape(
                bullet_match.group(1)
            )

            story.append(
                Paragraph(
                    f"• {bullet_text}",
                    bullet_style,
                )
            )

        else:
            story.append(
                Paragraph(
                    safe_line,
                    body_style,
                )
            )

    # Terms table
    terms = extract_terms(document_text)

    if terms:
        story.append(
            Spacer(1, 8)
        )

        story.append(
            Paragraph(
                "KEY TERMS AND CONDITIONS",
                heading_style,
            )
        )

        table_data = [
            [
                Paragraph(
                    "<b>No.</b>",
                    body_style,
                ),
                Paragraph(
                    "<b>Term / Condition</b>",
                    body_style,
                ),
            ]
        ]

        for index, term in enumerate(terms, start=1):
            table_data.append(
                [
                    Paragraph(
                        str(index),
                        body_style,
                    ),
                    Paragraph(
                        html.escape(term),
                        body_style,
                    ),
                ]
            )

        terms_table = Table(
            table_data,
            colWidths=[
                18 * mm,
                142 * mm,
            ],
            repeatRows=1,
        )

        terms_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(
            terms_table
        )

    # AI notice
    story.append(
        Paragraph(
            "AI DRAFT NOTICE: This document was generated "
            "by LegalEase using generative AI. It should be "
            "reviewed by a qualified legal professional "
            "before being signed or relied upon.",
            notice_style,
        )
    )

    document.build(
        story,
        onFirstPage=_add_pdf_header_footer,
        onLaterPages=_add_pdf_header_footer,
    )

    return output.getvalue()


# ---------------------------------------------------------
# PDF Header / Footer
# ---------------------------------------------------------

def _add_pdf_header_footer(canvas, doc):
    canvas.saveState()

    width, height = A4

    canvas.setFont(
        "Helvetica-Bold",
        9,
    )

    canvas.drawString(
        20 * mm,
        height - 15 * mm,
        "LegalEase",
    )

    canvas.setFont(
        "Helvetica",
        8,
    )

    canvas.drawRightString(
        width - 20 * mm,
        10 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


# ---------------------------------------------------------
# Compatibility Functions
# ---------------------------------------------------------

def format_docx(
    text: str,
    doc_type: str = "",
) -> bytes:
    return create_docx(text)


def format_pdf(
    text: str,
    doc_type: str = "",
) -> bytes:
    return create_pdf(text)