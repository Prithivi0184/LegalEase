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


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


st.title("⚖️ LegalEase")
st.subheader("AI-Powered Legal Document Generator")

st.write(
    "Create professional AI-generated legal document drafts "
    "from the information you provide."
)

st.divider()


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


if st.button(
    "⚡ Generate Legal Document",
    use_container_width=True,
):

    if not parties.strip():
        st.error("Please enter the parties involved.")

    elif not terms.strip():
        st.error("Please enter the terms and conditions.")

    elif not effective_date.strip():
        st.error("Please enter the effective date.")

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

                    st.success(
                        "Legal document generated successfully!"
                    )

                    st.divider()

                    st.markdown(
                        "### 📃 Generated Document"
                    )

                    st.text_area(
                        "Document",
                        document,
                        height=600,
                    )

                    txt_file = create_txt(
                        document
                    )

                    docx_file = create_docx(
                        document
                    )

                    pdf_file = create_pdf(
                        document
                    )

                    st.markdown(
                        "### 📥 Download Document"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.download_button(
                            label="📄 Download TXT",
                            data=txt_file,
                            file_name=(
                                "LegalEase_Legal_Document.txt"
                            ),
                            mime="text/plain",
                            use_container_width=True,
                        )

                    with col2:

                        st.download_button(
                            label="📝 Download DOCX",
                            data=docx_file,
                            file_name=(
                                "LegalEase_Legal_Document.docx"
                            ),
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
                            file_name=(
                                "LegalEase_Legal_Document.pdf"
                            ),
                            mime="application/pdf",
                            use_container_width=True,
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
                f"Unable to create the document files: {exc}"
            )


st.divider()


st.caption(
    "⚠️ LegalEase generates AI-assisted document drafts. "
    "Review all generated documents with a qualified legal "
    "professional before signing or relying upon them."
)