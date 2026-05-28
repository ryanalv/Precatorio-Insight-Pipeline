from app.schemas import DocumentCompletenessScore, PrecatorioInput
from app.services.validator import is_field_filled


SCORE_WEIGHTS = {
    "nome_credor": 15,
    "numero_processo": 20,
    "ente_devedor": 15,
    "valor_estimado": 20,
    "natureza": 10,
    "tribunal": 10,
    "data_prevista_pagamento": 10,
}


def calculate_completeness_score(data: PrecatorioInput) -> DocumentCompletenessScore:
    criterios = {
        field_name: points if is_field_filled(data, field_name) else 0
        for field_name, points in SCORE_WEIGHTS.items()
    }
    return DocumentCompletenessScore(score=sum(criterios.values()), criterios=criterios)
