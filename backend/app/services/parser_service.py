from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
    elif suffix == ".docx":
        doc = DocxDocument(str(file_path))
        text = "\n".join(p.text for p in doc.paragraphs).strip()
    elif suffix == ".txt":
        text = file_path.read_text(encoding="utf-8", errors="replace").strip()
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    if not text:
        raise ValueError("No text could be extracted from the document")

    return text
