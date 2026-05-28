ANALYSES_TABLE = "analyses"


CREATE_ANALYSES_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {ANALYSES_TABLE} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    dados_estruturados_json TEXT NOT NULL,
    score INTEGER NOT NULL,
    score_criterios_json TEXT NOT NULL,
    classificacao TEXT NOT NULL,
    pendencias_json TEXT NOT NULL,
    resumo_ia_json TEXT NOT NULL,
    texto_extraido_preview TEXT
);
"""
