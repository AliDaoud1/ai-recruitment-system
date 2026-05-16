import fitz  # PyMuPDF python -m pip install pymupdf
import re
from pathlib import Path

class PDFLoader:
    def load(self, path: str) -> str:
        doc = fitz.open(path)
        text = ""

        for page in doc:
            text += page.get_text() + "\n"

        return text


def normalize(text: str) -> str:
    return re.sub(r"[_\-.]", " ", text).lower().strip()


def resolve_candidate_file(candidate: str, data_dir: Path) -> str | None:
    candidate_norm = normalize(candidate)

    for path in data_dir.glob("*"):
        if not path.is_file():
            continue

        file_norm = normalize(path.stem)

        if candidate_norm in file_norm:
            return str(path.name)   # or str(path) if you prefer full path

    return None
