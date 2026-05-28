from __future__ import annotations

import re

from app.schemas import PrecatorioInput


FIELD_PATTERNS: dict[str, list[str]] = {
    "nome_credor": [r"nome\s+do\s+credor", r"credor"],
    "numero_processo": [r"n[úu]mero\s+do\s+processo", r"processo"],
    "tribunal": [r"tribunal"],
    "ente_devedor": [r"ente\s+devedor", r"devedor"],
    "valor_estimado": [r"valor\s+estimado", r"valor\s+do\s+precat[óo]rio", r"valor"],
    "tipo_precatorio": [r"tipo\s+de\s+precat[óo]rio", r"tipo\s+precat[óo]rio"],
    "natureza": [r"natureza"],
    "data_prevista_pagamento": [
        r"data\s+prevista\s+de\s+pagamento",
        r"data\s+prevista\s+pagamento",
        r"previs[aã]o\s+de\s+pagamento",
    ],
    "status_documental": [r"status\s+documental", r"documenta[cç][aã]o"],
    "observacoes": [r"observa[cç][õo]es?", r"obs"],
}


def parse_text_to_precatorio(text: str) -> PrecatorioInput:
    fields: dict[str, str | None] = {field: None for field in FIELD_PATTERNS}

    for line in _clean_lines(text):
        for field_name, patterns in FIELD_PATTERNS.items():
            if fields[field_name]:
                continue

            value = _extract_labeled_value(line, patterns)
            if value:
                fields[field_name] = value

    fields["numero_processo"] = fields["numero_processo"] or _find_process_number(text)
    fields["tribunal"] = fields["tribunal"] or _find_court(text)
    fields["valor_estimado"] = fields["valor_estimado"] or _find_money_value(text)
    fields["data_prevista_pagamento"] = fields["data_prevista_pagamento"] or _find_date(text)

    return PrecatorioInput(**fields)


def _clean_lines(text: str) -> list[str]:
    return [line.strip(" -\t") for line in text.splitlines() if line.strip()]


def _extract_labeled_value(line: str, label_patterns: list[str]) -> str | None:
    for label_pattern in label_patterns:
        match = re.search(rf"^\s*{label_pattern}\s*[:\-]\s*(?P<value>.+)$", line, re.IGNORECASE)
        if match:
            return match.group("value").strip()
    return None


def _find_process_number(text: str) -> str | None:
    match = re.search(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b", text)
    return match.group(0) if match else None


def _find_court(text: str) -> str | None:
    match = re.search(r"\b(TRF\d|TRT\d{1,2}|TJ[A-Z]{2}|STJ|STF)\b", text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _find_money_value(text: str) -> str | None:
    match = re.search(r"R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}", text)
    return match.group(0) if match else None


def _find_date(text: str) -> str | None:
    match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)
    return match.group(0) if match else None
