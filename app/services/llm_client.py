from __future__ import annotations

import json

from app.config import get_settings
from app.schemas import AIExecutiveSummary, DocumentCompletenessScore, PrecatorioInput


def generate_executive_summary(
    data: PrecatorioInput,
    score: DocumentCompletenessScore,
    classification: str,
    pendencias: list[str],
) -> AIExecutiveSummary:
    settings = get_settings()
    fallback_summary = _build_fallback_summary(data, score, classification, pendencias)

    if not settings.qwen_api_key or not settings.qwen_base_url:
        return AIExecutiveSummary(
            resumo=fallback_summary,
            gerado_por_ia=False,
            modelo=settings.qwen_model,
            avisos=["LLM não acionada: configure QWEN_API_KEY e QWEN_BASE_URL no arquivo .env."],
        )

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
        )

        completion = client.chat.completions.create(
            model=settings.qwen_model,
            messages=_build_messages(data, score, classification, pendencias),
            temperature=0.2,
        )
        content = completion.choices[0].message.content

        if not content:
            raise ValueError("Resposta vazia da LLM.")

        return AIExecutiveSummary(
            resumo=content.strip(),
            gerado_por_ia=True,
            modelo=settings.qwen_model,
        )
    except Exception as exc:
        return AIExecutiveSummary(
            resumo=fallback_summary,
            gerado_por_ia=False,
            modelo=settings.qwen_model,
            avisos=[f"LLM indisponível ({exc.__class__.__name__}). Resumo determinístico utilizado."],
        )


def _build_messages(
    data: PrecatorioInput,
    score: DocumentCompletenessScore,
    classification: str,
    pendencias: list[str],
) -> list[dict[str, str]]:
    payload = {
        "dados_estruturados": data.model_dump(mode="json"),
        "score_completude": score.model_dump(mode="json"),
        "classificacao_simulada": classification,
        "pendencias": pendencias,
    }

    return [
        {
            "role": "system",
            "content": (
                "Você é um assistente de triagem inicial de precatórios para um MVP educacional. "
                "Não emita parecer jurídico, não aprove crédito, não tome decisão final e não invente "
                "dados ausentes. Informe limitações quando houver lacunas. Responda em português do "
                "Brasil, com tom profissional, objetivo e seguro."
            ),
        },
        {
            "role": "user",
            "content": (
                "Gere um resumo executivo curto contendo: síntese do caso, principais dados identificados, "
                "pendências documentais, justificativa da classificação simulada e próximos passos sugeridos. "
                "Use apenas os dados abaixo.\n\n"
                f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
            ),
        },
    ]


def _build_fallback_summary(
    data: PrecatorioInput,
    score: DocumentCompletenessScore,
    classification: str,
    pendencias: list[str],
) -> str:
    pendencias_text = ", ".join(pendencias) if pendencias else "sem pendências mínimas identificadas"
    valor = f"R$ {data.valor_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if data.valor_estimado else "não informado"

    return (
        "Resumo executivo gerado por regra determinística do MVP. "
        f"O caso envolve o credor {data.nome_credor or 'não informado'}, processo "
        f"{data.numero_processo or 'não informado'}, contra {data.ente_devedor or 'ente devedor não informado'}, "
        f"com valor estimado de {valor}. "
        f"O score de completude documental é {score.score}/100 e a classificação simulada é "
        f"'{classification}'. Pendências: {pendencias_text}. "
        "Próximos passos sugeridos: revisar os campos pendentes, confirmar a documentação de suporte e "
        "encaminhar para avaliação humana especializada. Este resumo não constitui parecer jurídico nem "
        "decisão de crédito."
    )
