from io import BytesIO

import pymupdf
from docx import Document
from pptx import Presentation


def extract_text_from_docx(file):
    document = Document(BytesIO(file.getvalue()))
    units = []
    for paragraph_number, paragraph in enumerate(document.paragraphs, start=1):
        if paragraph.text.strip():
            units.append(
                {
                    "file": file.name,
                    "source": f"paragraph {paragraph_number}",
                    "text": paragraph.text.strip(),
                }
            )
    for table_number, table in enumerate(document.tables, start=1):
        for row_number, row in enumerate(table.rows, start=1):
            text = " | ".join(cell.text.strip() for cell in row.cells).strip()
            if text:
                units.append(
                    {
                        "file": file.name,
                        "source": f"table {table_number}, row {row_number}",
                        "text": text,
                    }
                )
    return units


def extract_text_from_pptx(file):
    presentation = Presentation(BytesIO(file.getvalue()))
    units = []
    for slide_number, slide in enumerate(presentation.slides, start=1):
        slide_text = []
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                slide_text.append(shape.text.strip())
        if slide_text:
            units.append(
                {
                    "file": file.name,
                    "source": f"slide {slide_number}",
                    "text": "\n".join(slide_text),
                }
            )
    return units


def extract_text_from_files(files):
    document_units = []
    for file in files:
        filename = file.name.lower()
        if filename.endswith(".pdf"):
            with pymupdf.open(stream=file.getvalue(), filetype="pdf") as document:
                for page_number, page in enumerate(document, start=1):
                    text = page.get_text().strip()
                    if text:
                        document_units.append(
                            {
                                "file": file.name,
                                "source": f"page {page_number}",
                                "text": text,
                            }
                        )
        elif filename.endswith(".docx"):
            document_units.extend(extract_text_from_docx(file))
        elif filename.endswith(".pptx"):
            document_units.extend(extract_text_from_pptx(file))
    return document_units
