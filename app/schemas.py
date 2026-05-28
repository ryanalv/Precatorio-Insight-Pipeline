from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PrecatorioInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome_credor: str | None = None
    numero_processo: str | None = None
    tribunal: str | None = None
    ente_devedor: str | None = None
    valor_estimado: float | None = Field(default=None, ge=0)
    tipo_precatorio: str | None = None
    natureza: str | None = None
    data_prevista_pagamento: str | None = None
    status_documental: str | None = None
    observacoes: str | None = None

    @field_validator("*", mode="before")
    @classmethod
    def blank_strings_to_none(cls, value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @field_validator("valor_estimado", mode="before")
    @classmethod
    def parse_brazilian_money(cls, value: Any) -> Any:
        if value is None or isinstance(value, int | float):
            return value

        if isinstance(value, str):
            normalized = value.replace("R$", "").replace(" ", "").strip()
            if not normalized:
                return None
            if "," in normalized:
                normalized = normalized.replace(".", "").replace(",", ".")
            try:
                return float(normalized)
            except ValueError:
                return None

        return value


class DocumentCompletenessScore(BaseModel):
    score: int = Field(ge=0, le=100)
    criterios: dict[str, int]


class AIExecutiveSummary(BaseModel):
    resumo: str
    gerado_por_ia: bool
    modelo: str | None = None
    avisos: list[str] = Field(default_factory=list)


class PrecatorioAnalysis(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    dados_estruturados: PrecatorioInput
    score_completude: DocumentCompletenessScore
    classificacao: str
    pendencias: list[str]
    resumo_ia: AIExecutiveSummary
    texto_extraido_preview: str | None = None
