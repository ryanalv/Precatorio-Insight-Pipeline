from __future__ import annotations

from datetime import datetime, timezone
import json
import sqlite3

from app.config import get_settings
from app.models import ANALYSES_TABLE, CREATE_ANALYSES_TABLE_SQL
from app.schemas import AIExecutiveSummary, DocumentCompletenessScore, PrecatorioAnalysis, PrecatorioInput


def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(CREATE_ANALYSES_TABLE_SQL)
        connection.commit()


def save_analysis(analysis: PrecatorioAnalysis) -> PrecatorioAnalysis:
    init_db()
    created_at = datetime.now(timezone.utc)

    with get_connection() as connection:
        cursor = connection.execute(
            f"""
            INSERT INTO {ANALYSES_TABLE} (
                created_at,
                dados_estruturados_json,
                score,
                score_criterios_json,
                classificacao,
                pendencias_json,
                resumo_ia_json,
                texto_extraido_preview
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at.isoformat(),
                json.dumps(analysis.dados_estruturados.model_dump(mode="json"), ensure_ascii=False),
                analysis.score_completude.score,
                json.dumps(analysis.score_completude.criterios, ensure_ascii=False),
                analysis.classificacao,
                json.dumps(analysis.pendencias, ensure_ascii=False),
                json.dumps(analysis.resumo_ia.model_dump(mode="json"), ensure_ascii=False),
                analysis.texto_extraido_preview,
            ),
        )
        connection.commit()
        analysis_id = int(cursor.lastrowid)

    return analysis.model_copy(update={"id": analysis_id, "created_at": created_at})


def list_analyses(limit: int = 50) -> list[PrecatorioAnalysis]:
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            f"SELECT * FROM {ANALYSES_TABLE} ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [_row_to_analysis(row) for row in rows]


def get_analysis(analysis_id: int) -> PrecatorioAnalysis | None:
    init_db()
    with get_connection() as connection:
        row = connection.execute(
            f"SELECT * FROM {ANALYSES_TABLE} WHERE id = ?",
            (analysis_id,),
        ).fetchone()

    return _row_to_analysis(row) if row else None


def _row_to_analysis(row: sqlite3.Row) -> PrecatorioAnalysis:
    return PrecatorioAnalysis(
        id=int(row["id"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        dados_estruturados=PrecatorioInput(**json.loads(row["dados_estruturados_json"])),
        score_completude=DocumentCompletenessScore(
            score=int(row["score"]),
            criterios=json.loads(row["score_criterios_json"]),
        ),
        classificacao=row["classificacao"],
        pendencias=json.loads(row["pendencias_json"]),
        resumo_ia=AIExecutiveSummary(**json.loads(row["resumo_ia_json"])),
        texto_extraido_preview=row["texto_extraido_preview"],
    )
