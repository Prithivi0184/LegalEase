import html
import os

import requests
import streamlit as st
from dotenv import load_dotenv

from utils.document_export import (
    create_docx,
    create_pdf,
    create_txt,
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# =========================================================
# HEADER STYLING
# =========================================================

st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #888888;
            margin-bottom: 25px;
        }

        .notice-box {
            background-color: #332b16;
            border: 1px solid #66551f;
            border-radius: 8px;
            padding: 14px;
            margin-top: 18px;
            color: #f5df8a;
            font-size: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True,
)

st.write(
    "Create professional AI-generated legal document drafts "
    "from the information you provide."
)

st.divider()


# =========================================================
# DOCUMENT DETAILS
# =========================================================

st.markdown("### 📄 Document Details")


document_type = st.selectbox(
    "Document Type",
    [
        "Rental Agreement",
        "Employment Agreement",
        "Non-Disclosure Agreement",
        "Service Agreement",
        "Freelance Agreement",
        "Partnership Agreement",
        "Other",
    ],
)


parties = st.text_area(
    "Parties",
    placeholder=(
        "Example: Landlord: Arun Kumar; "
        "Tenant: Ravi Kumar"
    ),
    height=100,
)


terms = st.text_area(
    "Terms and Conditions",
    placeholder=(
        "Enter the important terms, obligations, "
        "payments, responsibilities, etc."
    ),
    height=180,
)


effective_date = st.text_input(
    "Effective Date",
    placeholder="Example: 1 October 2026",
)


st.divider()


# =========================================================
# GENERATE DOCUMENT
# =========================================================

if st.button(
    "⚡ Generate Legal Document",
    use_container_width=True,
):

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

    elif not effective_date.strip():

        st.error(
            "Please enter the effective date."
        )

    else:

        request_data = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
        }

        try:

            with st.spinner(
                "Generating your legal document with AI..."
            ):

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=request_data,
                    timeout=120,
                )

            if response.status_code == 200:

                result = response.json()

                document = result.get(
                    "document",
                    "",
                )

                if document:

                    st.session_state[
                        "generated_document"
                    ] = document

                    st.session_state[
                        "edited_document"
                    ] = document

                    st.session_state[
                        "editing"
                    ] = False

                    st.success(
                        "Legal document generated successfully!"
                    )

                else:

                    st.error(
                        "The backend returned an empty document."
                    )

            else:

                try:

                    error_detail = response.json().get(
                        "detail",
                        "Unknown backend error.",
                    )

                except ValueError:

                    error_detail = response.text

                st.error(
                    f"Document generation failed: "
                    f"{error_detail}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the LegalEase backend. "
                "Make sure the FastAPI server is running."
            )

        except requests.exceptions.Timeout:

            st.error(
                "The AI generation request timed out. "
                "Please try again."
            )

        except requests.exceptions.RequestException as exc:

            st.error(
                f"Unable to contact the backend: {exc}"
            )

        except Exception as exc:

            st.error(
                f"An unexpected error occurred: {exc}"
            )


# =========================================================
# GENERATED DOCUMENT
# =========================================================

if "generated_document" in st.session_state:

    st.divider()

    st.markdown("### 📃 Generated Document")


    # =====================================================
    # EDIT / PREVIEW BUTTONS
    # =====================================================

    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "✏️ Edit Document",
            use_container_width=True,
        ):

            st.session_state[
                "editing"
            ] = True


    with col2:

        if st.button(
            "👁️ Preview Document",
            use_container_width=True,
        ):

            st.session_state[
                "editing"
            ] = False


    # =====================================================
    # EDIT MODE
    # =====================================================

    if st.session_state.get(
        "editing",
        False,
    ):

        edited_document = st.text_area(
            "Edit your document",
            value=st.session_state.get(
                "edited_document",
                st.session_state[
                    "generated_document"
                ],
            ),
            height=650,
        )

        st.session_state[
            "edited_document"
        ] = edited_document

        st.info(
            "You can modify the generated document "
            "before downloading it."
        )


    # =====================================================
    # PREVIEW MODE
    # =====================================================

    else:

        document_to_preview = st.session_state.get(
            "edited_document",
            st.session_state[
                "generated_document"
            ],
        )

        # Escape AI-generated content.
        # This prevents generated text from being
        # interpreted as HTML.
        escaped_document = html.escape(
            document_to_preview
        )

        # Use native Streamlit HTML rendering.
        # This avoids the previous <div> rendering issue.
        preview_html = f"""
        <style>

            .legal-preview-wrapper {{
                width: 100%;
            }}

            .legal-preview-title {{
                color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 22px;
                font-weight: 700;
                margin-bottom: 15px;
            }}

            .legal-preview-card {{
                background: #151515;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 30px;
                height: 650px;
                overflow-y: auto;
                color: #eeeeee;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 16px;
                line-height: 1.75;
                white-space: pre-wrap;
                word-wrap: break-word;
                box-sizing: border-box;
            }}

        </style>

        <div class="legal-preview-wrapper">

            <div class="legal-preview-title">
                ⚖️ LegalEase Document Preview
            </div>

            <div class="legal-preview-card">{escaped_document}</div>

        </div>
        """

        st.html(preview_html)


    # =====================================================
    # DOWNLOAD SECTION
    # =====================================================

    st.markdown("### 📥 Download Document")


    final_document = st.session_state.get(
        "edited_document",
        st.session_state[
            "generated_document"
        ],
    )


    txt_file = create_txt(
        final_document
    )

    docx_file = create_docx(
        final_document
    )

    pdf_file = create_pdf(
        final_document
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.download_button(
            label="📄 Download TXT",
            data=txt_file,
            file_name="LegalEase_Legal_Document.txt",
            mime="text/plain",
            use_container_width=True,
        )


    with col2:

        st.download_button(
            label="📝 Download DOCX",
            data=docx_file,
            file_name="LegalEase_Legal_Document.docx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            use_container_width=True,
        )


    with col3:

        st.download_button(
            label="📕 Download PDF",
            data=pdf_file,
            file_name="LegalEase_Legal_Document.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


    # =====================================================
    # AI DRAFT NOTICE
    # =====================================================

    st.markdown(
        """
        <div class="notice-box">
            ⚠️ <strong>AI Draft Notice:</strong>
            This document was generated by LegalEase using
            generative AI. It should be reviewed by a qualified
            legal professional before being signed or relied upon.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "LegalEase — AI-assisted legal document drafting. "
    "Review generated documents with a qualified legal "
    "professional before signing or relying upon them."
)