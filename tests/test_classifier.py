from app.schemas import PrecatorioInput
from app.services.classifier import (
    CLASS_ALTA,
    CLASS_DADOS_INSUFICIENTES,
    CLASS_FORA_PERFIL,
    CLASS_MEDIA,
    CLASS_REVISAO,
    classify_precatorio,
)


def test_classify_data_insufficient_when_score_is_low() -> None:
    data = PrecatorioInput(valor_estimado=100000)

    assert classify_precatorio(data, score=35, pendencias=["nome_credor"]) == CLASS_DADOS_INSUFICIENTES


def test_classify_outside_profile_when_value_is_low() -> None:
    data = PrecatorioInput(valor_estimado=30000)

    assert classify_precatorio(data, score=90, pendencias=[]) == CLASS_FORA_PERFIL


def test_classify_high_priority() -> None:
    data = PrecatorioInput(valor_estimado=150000)

    assert classify_precatorio(data, score=85, pendencias=[]) == CLASS_ALTA


def test_classify_medium_priority() -> None:
    data = PrecatorioInput(valor_estimado=150000)

    assert classify_precatorio(data, score=70, pendencias=[]) == CLASS_MEDIA


def test_classify_document_review_when_required_fields_are_pending() -> None:
    data = PrecatorioInput(valor_estimado=150000)

    assert classify_precatorio(data, score=90, pendencias=["status_documental"]) == CLASS_REVISAO
