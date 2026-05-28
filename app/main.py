from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes.analysis_routes import router as analysis_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Precatorio Insight Pipeline",
    version="0.1.0",
    description="MVP educacional para triagem inicial simulada de precatórios.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "precatorio-insight-pipeline",
        "message": "API disponível para triagem inicial simulada de precatórios.",
    }


app.include_router(analysis_router)
