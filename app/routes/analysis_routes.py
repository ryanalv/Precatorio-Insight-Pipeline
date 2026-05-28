from fastapi import APIRouter, File, HTTPException, UploadFile

from app.database import get_analysis, list_analyses
from app.schemas import PrecatorioAnalysis, PrecatorioInput
from app.services.analyzer import analyze_extracted_text, analyze_precatorio
from app.services.pdf_extractor import extract_text_from_pdf


router = APIRouter(tags=["analyses"])


@router.post("/analyze/manual", response_model=PrecatorioAnalysis)
def analyze_manual(payload: PrecatorioInput) -> PrecatorioAnalysis:
    return analyze_precatorio(payload)


@router.post("/analyze/pdf", response_model=PrecatorioAnalysis)
async def analyze_pdf(file: UploadFile = File(...)) -> PrecatorioAnalysis:
    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")

    try:
        file_bytes = await file.read()
        extracted_text = extract_text_from_pdf(file_bytes)
        return analyze_extracted_text(extracted_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/analyses", response_model=list[PrecatorioAnalysis])
def read_analyses() -> list[PrecatorioAnalysis]:
    return list_analyses()


@router.get("/analyses/{analysis_id}", response_model=PrecatorioAnalysis)
def read_analysis(analysis_id: int) -> PrecatorioAnalysis:
    analysis = get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return analysis
