from app.database import save_analysis
from app.schemas import PrecatorioAnalysis, PrecatorioInput
from app.services.classifier import classify_precatorio
from app.services.field_parser import parse_text_to_precatorio
from app.services.llm_client import generate_executive_summary
from app.services.scorer import calculate_completeness_score
from app.services.validator import validate_required_fields


def analyze_precatorio(
    data: PrecatorioInput,
    extracted_text: str | None = None,
    persist: bool = True,
) -> PrecatorioAnalysis:
    pendencias = validate_required_fields(data)
    score = calculate_completeness_score(data)
    classification = classify_precatorio(data, score.score, pendencias)
    summary = generate_executive_summary(data, score, classification, pendencias)

    analysis = PrecatorioAnalysis(
        dados_estruturados=data,
        score_completude=score,
        classificacao=classification,
        pendencias=pendencias,
        resumo_ia=summary,
        texto_extraido_preview=_build_text_preview(extracted_text),
    )

    return save_analysis(analysis) if persist else analysis


def analyze_extracted_text(text: str) -> PrecatorioAnalysis:
    parsed_data = parse_text_to_precatorio(text)
    return analyze_precatorio(parsed_data, extracted_text=text)


def _build_text_preview(text: str | None, limit: int = 1200) -> str | None:
    if not text:
        return None

    compact = " ".join(text.split())
    return compact[:limit]
