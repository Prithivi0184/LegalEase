from fastapi import APIRouter
from pydantic import BaseModel, Field

from .config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    application: str
    version: str


class GenerateRequest(BaseModel):
    document_type: str = Field(
        ...,
        min_length=1,
        description="Type of legal document to generate",
    )
    parties: str = Field(
        ...,
        min_length=1,
        description="People or organizations involved",
    )
    terms: str = Field(
        ...,
        min_length=1,
        description="Important terms and conditions",
    )
    effective_date: str = Field(
        ...,
        min_length=1,
        description="Effective date of the document",
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check whether the LegalEase backend is running.
    """
    return HealthResponse(
        status="healthy",
        application=settings.app_name,
        version="2.0.0",
    )


@router.get("/")
async def root():
    """
    Basic API information.
    """
    return {
        "application": settings.app_name,
        "message": "LegalEase API is running",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@router.post("/generate")
async def generate_document(request: GenerateRequest):
    """
    Phase 2 placeholder for document generation.

    Gemini integration will be added in Phase 3.
    """
    return {
        "success": True,
        "phase": 2,
        "message": "Request received successfully. AI generation will be connected in Phase 3.",
        "request": {
            "document_type": request.document_type,
            "parties": request.parties,
            "terms": request.terms,
            "effective_date": request.effective_date,
        },
    }