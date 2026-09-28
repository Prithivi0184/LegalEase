from fastapi.testclient import TestClient

from backend.main import app
from utils.document_export import (
    sanitize_text,
    format_html_preview,
    create_txt,
    create_docx,
    create_pdf,
)


client = TestClient(app)


# =========================================================
# BACKEND TESTS
# =========================================================

def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "LegalEase"
    assert data["message"] == "LegalEase API is running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["application"] == "LegalEase"


def test_generate_validation():
    response = client.post(
        "/generate",
        json={
            "document_type": "",
            "parties": "Landlord: Arun Kumar; Tenant: Ravi Kumar",
            "terms": "Monthly rent: ₹15000",
            "effective_date": "1 October 2026",
        },
    )

    assert response.status_code == 422


# =========================================================
# TEXT SANITIZATION TESTS
# =========================================================

def test_sanitize_text():
    text = (
        "This is a “legal” document — "
        "with special characters…"
    )

    cleaned = sanitize_text(text)

    assert "“" not in cleaned
    assert "”" not in cleaned
    assert "—" not in cleaned
    assert "…" not in cleaned

    assert '"legal"' in cleaned
    assert "-" in cleaned
    assert "..." in cleaned


# =========================================================
# HTML PREVIEW TESTS
# =========================================================

def test_format_html_preview():
    document = """
    RENTAL AGREEMENT

    1. PARTIES

    Landlord: Arun Kumar
    Tenant: Ravi Kumar

    • Monthly rent: ₹15000
    """

    preview = format_html_preview(document)

    assert "legal-preview-card" in preview
    assert "RENTAL AGREEMENT" in preview
    assert "1. PARTIES" in preview
    assert "Monthly rent: ₹15000" in preview


def test_html_preview_escapes_html():
    document = "<script>alert('test')</script>"

    preview = format_html_preview(document)

    assert "<script>" not in preview
    assert "&lt;script&gt;" in preview


# =========================================================
# EXPORT TESTS
# =========================================================

def test_create_txt():
    document = "RENTAL AGREEMENT\nLandlord: Arun Kumar"

    result = create_txt(document)

    assert isinstance(result, bytes)
    assert b"RENTAL AGREEMENT" in result


def test_create_docx():
    document = "RENTAL AGREEMENT\nLandlord: Arun Kumar"

    result = create_docx(document)

    assert isinstance(result, bytes)
    assert result.startswith(
        b"PK"
    )


def test_create_pdf():
    document = "RENTAL AGREEMENT\nLandlord: Arun Kumar"

    result = create_pdf(document)

    assert isinstance(result, bytes)
    assert result.startswith(
        b"%PDF"
    )