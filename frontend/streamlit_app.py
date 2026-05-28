from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import requests
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


st.set_page_config(
    page_title="Precatorio Insight Pipeline",
    page_icon="PI",
    layout="wide",
)


def post_manual_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{API_BASE_URL}/analyze/manual", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def post_pdf_analysis(file_name: str, file_bytes: bytes) -> dict[str, Any]:
    files = {"file": (file_name, file_bytes, "application/pdf")}
    response = requests.post(f"{API_BASE_URL}/analyze/pdf", files=files, timeout=90)
    response.raise_for_status()
    return response.json()


def fetch_history() -> list[dict[str, Any]]:
    response = requests.get(f"{API_BASE_URL}/analyses", timeout=20)
    response.raise_for_status()
    return response.json()


def none_if_blank(value: Any) -> Any:
    if isinstance(value, str) and not value.strip():
        return None
    return value


def render_analysis(analysis: dict[str, Any]) -> None:
    st.subheader("Resultado da análise")

    score = analysis["score_completude"]["score"]
    classification = analysis["classificacao"]
    pending = analysis["pendencias"]
    summary = analysis["resumo_ia"]

    metric_col, class_col, llm_col = st.columns(3)
    metric_col.metric("Score de completude", f"{score}/100")
    class_col.metric("Classificação simulada", classification)
    llm_col.metric("Resumo", "IA" if summary["gerado_por_ia"] else "Fallback")

    st.markdown("**Campos estruturados**")
    st.json(analysis["dados_estruturados"])

    st.markdown("**Pendências**")
    if pending:
        st.warning(", ".join(pending))
    else:
        st.success("Nenhuma pendência mínima identificada.")

    st.markdown("**Resumo executivo**")
    st.write(summary["resumo"])

    for warning in summary.get("avisos", []):
        st.info(warning)

    if analysis.get("texto_extraido_preview"):
        with st.expander("Prévia do texto extraído"):
            st.write(analysis["texto_extraido_preview"])


def render_history() -> None:
    st.subheader("Histórico de análises")
    try:
        analyses = fetch_history()
    except requests.RequestException as exc:
        st.info(f"Histórico indisponível: {exc}")
        return

    if not analyses:
        st.caption("Nenhuma análise salva ainda.")
        return

    for item in analyses[:10]:
        title = f"#{item['id']} - {item['classificacao']} - score {item['score_completude']['score']}/100"
        with st.expander(title):
            st.write(item["created_at"])
            st.json(item["dados_estruturados"])
            st.write(item["resumo_ia"]["resumo"])


st.title("Precatorio Insight Pipeline")
st.write(
    "MVP educacional para triagem inicial simulada de precatórios, com validação de dados, "
    "score documental, classificação transparente e resumo executivo com IA generativa."
)
st.caption("Não substitui análise jurídica, comercial ou de crédito feita por especialistas.")

manual_tab, pdf_tab, history_tab = st.tabs(["Entrada manual", "Upload de PDF", "Histórico"])

with manual_tab:
    with st.form("manual_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            nome_credor = st.text_input("Nome do credor")
            numero_processo = st.text_input("Número do processo")
            tribunal = st.text_input("Tribunal")
            ente_devedor = st.text_input("Ente devedor")
            valor_estimado = st.number_input("Valor estimado", min_value=0.0, step=1000.0, format="%.2f")
        with col_b:
            tipo_precatorio = st.text_input("Tipo de precatório")
            natureza = st.selectbox("Natureza", ["", "Alimentar", "Comum", "Outra"])
            data_prevista_pagamento = st.text_input("Data prevista de pagamento")
            status_documental = st.selectbox(
                "Status documental",
                ["", "Completo", "Parcial", "Pendente", "Não informado"],
            )
            observacoes = st.text_area("Observações", height=112)

        submitted = st.form_submit_button("Analisar precatório", type="primary")

    if submitted:
        payload = {
            "nome_credor": none_if_blank(nome_credor),
            "numero_processo": none_if_blank(numero_processo),
            "tribunal": none_if_blank(tribunal),
            "ente_devedor": none_if_blank(ente_devedor),
            "valor_estimado": valor_estimado if valor_estimado > 0 else None,
            "tipo_precatorio": none_if_blank(tipo_precatorio),
            "natureza": none_if_blank(natureza),
            "data_prevista_pagamento": none_if_blank(data_prevista_pagamento),
            "status_documental": none_if_blank(status_documental),
            "observacoes": none_if_blank(observacoes),
        }

        try:
            render_analysis(post_manual_analysis(payload))
        except requests.RequestException as exc:
            st.error(f"Não foi possível chamar a API: {exc}")

with pdf_tab:
    uploaded_file = st.file_uploader("PDF simulado de precatório", type=["pdf"])
    analyze_pdf = st.button("Analisar PDF", type="primary", disabled=uploaded_file is None)

    if analyze_pdf and uploaded_file is not None:
        try:
            render_analysis(post_pdf_analysis(uploaded_file.name, uploaded_file.getvalue()))
        except requests.RequestException as exc:
            st.error(f"Não foi possível analisar o PDF: {exc}")

with history_tab:
    render_history()
