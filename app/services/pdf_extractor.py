from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not file_bytes:
        raise ValueError("Arquivo PDF vazio.")

    reader = PdfReader(BytesIO(file_bytes))
    extracted_pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(extracted_pages).strip()

    if not text:
        raise ValueError("Não foi possível extrair texto do PDF enviado.")

    return text
