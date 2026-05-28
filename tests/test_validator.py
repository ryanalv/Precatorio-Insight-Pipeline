from app.schemas import PrecatorioInput
from app.services.validator import validate_required_fields


def test_validate_required_fields_returns_missing_fields() -> None:
    data = PrecatorioInput(nome_credor="Maria Silva", valor_estimado=120000)

    pendencias = validate_required_fields(data)

    assert "nome_credor" not in pendencias
    assert "valor_estimado" not in pendencias
    assert "numero_processo" in pendencias
    assert "ente_devedor" in pendencias
    assert "natureza" in pendencias
    assert "status_documental" in pendencias


def test_validate_required_fields_accepts_complete_record() -> None:
    data = PrecatorioInput(
        nome_credor="Maria Silva",
        numero_processo="1234567-89.2024.8.26.0053",
        ente_devedor="Estado de São Paulo",
        valor_estimado=120000,
        natureza="Alimentar",
        status_documental="Completo",
    )

    assert validate_required_fields(data) == []
