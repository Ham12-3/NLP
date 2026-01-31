from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .schemas import CorrectionRequest, CorrectionResponse
from .corrector import get_corrector

app = FastAPI(
    title="Text Corrector API",
    description="Corrects grammar and converts text between British and American English.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/correct", response_model=CorrectionResponse)
def correct_text(req: CorrectionRequest) -> CorrectionResponse:
    corrector = get_corrector()
    corrected, changes = corrector.correct(req.text, req.variant)
    return CorrectionResponse(
        corrected=corrected,
        variant=req.variant,
        changes=changes,
    )
