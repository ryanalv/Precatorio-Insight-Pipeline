from app.schemas import PrecatorioInput


CLASS_DADOS_INSUFICIENTES = "Dados insuficientes"
CLASS_FORA_PERFIL = "Fora do perfil simulado"
CLASS_REVISAO = "Necessita revisão documental"
CLASS_MEDIA = "Média prioridade"
CLASS_ALTA = "Alta prioridade comercial"


def classify_precatorio(data: PrecatorioInput, score: int, pendencias: list[str] | None = None) -> str:
    valor_estimado = data.valor_estimado or 0

    if score < 50 or valor_estimado <= 0:
        return CLASS_DADOS_INSUFICIENTES
    if valor_estimado < 50_000:
        return CLASS_FORA_PERFIL
    if pendencias:
        return CLASS_REVISAO
    if score >= 75:
        return CLASS_ALTA
    if score >= 65:
        return CLASS_MEDIA

    return CLASS_REVISAO
