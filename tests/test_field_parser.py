import pytest

from app.services.field_parser import parse_text_to_precatorio


def test_parse_labeled_fields_with_common_variations() -> None:
    text = """
    Parte Credora: Joao da Silva
    Nº do Processo: 1234567-89.2024.8.26.0053
    Tribunal: TRF6
    Entidade Devedora: Uniao Federal
    Valor Requisitado: 185.000,00
    Natureza do Credito: Alimentar
    Previsao de Pagamento: 2026
    Documentacao: Parcial
    """

    data = parse_text_to_precatorio(text)

    assert data.nome_credor == "Joao da Silva"
    assert data.numero_processo == "1234567-89.2024.8.26.0053"
    assert data.tribunal == "TRF6"
    assert data.ente_devedor == "Uniao Federal"
    assert data.valor_estimado == 185000.0
    assert data.natureza == "Alimentar"
    assert data.data_prevista_pagamento == "2026"
    assert data.status_documental == "Parcial"


def test_parse_unlabeled_process_number_and_court() -> None:
    text = "Processo 1234567-89.2024.8.26.0053 em tramitacao no TRF6."

    data = parse_text_to_precatorio(text)

    assert data.numero_processo == "1234567-89.2024.8.26.0053"
    assert data.tribunal == "TRF6"


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("R$ 185.000,00", 185000.0),
        ("185.000,00", 185000.0),
        ("185000,00", 185000.0),
        ("185000.00", 185000.0),
    ],
)
def test_parse_brazilian_money_variants(raw_value: str, expected: float) -> None:
    data = parse_text_to_precatorio(f"Valor do Precatorio: {raw_value}")

    assert data.valor_estimado == expected
