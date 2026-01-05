from __future__ import annotations

from pathlib import Path
import pdfplumber


class TextExtractionError(RuntimeError):
    pass


def extract_text_from_pdf(file_path: str) -> str:
    path = Path(file_path)
    lines: list[str] = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    lines.append(t)
    except Exception as e:
        raise TextExtractionError("Failed to extract text from PDF.") from e
    return "\n".join(lines).strip()


def extract_text_from_txt(file_path: str) -> str:
    path = Path(file_path)
    try:
        return path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1").strip()


def extract_text_from_file(file_path: str) -> str:
    fp = str(file_path)
    if fp.lower().endswith(".pdf"):
        return extract_text_from_pdf(fp)
    if fp.lower().endswith(".txt"):
        return extract_text_from_txt(fp)
    raise ValueError("Only .pdf or .txt files are supported.")
