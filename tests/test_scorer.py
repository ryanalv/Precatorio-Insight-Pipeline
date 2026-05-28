from app.schemas import PrecatorioInput
from app.services.scorer import calculate_completeness_score


def test_calculate_completeness_score_full_record() -> None:
    data = PrecatorioInput(
        nome_credor="Maria Silva",
        numero_processo="1234567-89.2024.8.26.0053",
        tribunal="TJSP",
        ente_devedor="Estado de São Paulo",
        valor_estimado=120000,
        natureza="Alimentar",
        data_prevista_pagamento="31/12/2026",
        status_documental="Completo",
    )

    score = calculate_completeness_score(data)

    assert score.score == 100
    assert score.criterios["numero_processo"] == 20


def test_calculate_completeness_score_partial_record() -> None:
    data = PrecatorioInput(
        nome_credor="Maria Silva",
        valor_estimado=120000,
        status_documental="Parcial",
    )

    score = calculate_completeness_score(data)

    assert score.score == 35
    assert score.criterios["nome_credor"] == 15
    assert score.criterios["valor_estimado"] == 20
    assert score.criterios["tribunal"] == 0
