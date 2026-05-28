from app.config import get_settings
from app.schemas import PrecatorioInput
from app.services.llm_client import generate_executive_summary
from app.services.scorer import calculate_completeness_score


def test_generate_executive_summary_uses_deterministic_fallback_when_llm_is_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    monkeypatch.delenv("QWEN_BASE_URL", raising=False)
    monkeypatch.setenv("QWEN_MODEL", "qwen/qwen3-14b")
    get_settings.cache_clear()

    try:
        data = PrecatorioInput(
            nome_credor="Maria Silva",
            numero_processo="1234567-89.2024.8.26.0053",
            tribunal="TJSP",
            ente_devedor="Estado de Sao Paulo",
            valor_estimado=185000,
            natureza="Alimentar",
            status_documental="Parcial",
        )
        score = calculate_completeness_score(data)

        summary = generate_executive_summary(
            data=data,
            score=score,
            classification="Alta prioridade comercial",
            pendencias=[],
        )

        assert summary.gerado_por_ia is False
        assert summary.modelo == "qwen/qwen3-14b"
        assert summary.avisos
        assert "Resumo executivo gerado por regra determin" in summary.resumo
    finally:
        get_settings.cache_clear()
