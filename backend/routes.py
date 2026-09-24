from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .config import settings
from ai_core.gemini_generator import (
    GeminiGenerationError,
    generate_legal_document,
)

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
    return HealthResponse(
        status="healthy",
        application=settings.app_name,
        version="3.0.0",
    )


@router.get("/")
async def root():
    return {
        "application": settings.app_name,
        "message": "LegalEase API is running",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@router.post("/generate")
async def generate_document(request: GenerateRequest):
    try:
        document = generate_legal_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
        )

        return {
            "success": True,
            "phase": 3,
            "document": document,
        }

    except GeminiGenerationError as exc:
        raise HTTPException(
            status_code=503,
            detail="AI document generation is currently unavailable.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating the document.",
        ) from exc