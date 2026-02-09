import streamlit as st
import requests
from PIL import Image

st.set_page_config(
    page_title="Document Extractor",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------- Styling -------------------
st.markdown("""
<style>
body { background-color: #f0f8ff; color: #333; font-family: 'Segoe UI', sans-serif; }
.stButton>button { background-color: #f5f5dc; color: #333; border-radius: 8px; border: 1px solid #aaa; padding: 0.5em 1em; font-weight: bold; }
.missing-field { color: red; font-weight: bold; }
.stTextInput>div>input { border-radius: 6px; border: 1px solid #aaa; padding: 0.3em; }
</style>
""", unsafe_allow_html=True)

# ------------------- Title -------------------
st.title("📄 AI Document Extractor")
st.subheader("Upload Aadhaar, PAN, Passport or any ID document")

# ------------------- File Upload -------------------
uploaded_file = st.file_uploader(
    "Choose a document image (JPEG/PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    # Show image preview
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Document", width=600)

    st.info("Processing document... please wait")
    file_bytes = uploaded_file.getvalue()

    # ------------------- Call backend API -------------------
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/documents/extract",
            files={"file": (uploaded_file.name, file_bytes)}
        )
        result = response.json()
    except Exception as e:
        st.error(f"Failed to call extraction API: {e}")
    else:
        data = result.get("data", {})
        confidence = result.get("confidence", 0)
        hitl_required = result.get("hitl_required", False)
        prompt = result.get("prompt", "")

        doc_type = data.get("document_type", "Unknown")

        # ------------------- Display document info -------------------
        st.success(f"Document Type: {doc_type}")
        st.info(f"Confidence: {confidence:.2f} | HITL Required: {hitl_required}")

        st.subheader("Extracted Fields")
        for key, value in data.items():
            if not value:
                st.markdown(
                    f"{key}: <span class='missing-field'>MISSING / INVALID</span>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f"{key}: {value}")

        # ------------------- HITL Section (ONLY if required) -------------------
        if hitl_required:
            st.warning(
                "Some required fields are missing or document type is unknown. "
                "Please provide the correct information:"
            )

            hitl_fields = {}
            for field in ["name", "date_of_birth", "document_number", "address"]:
                value = data.get(field)
                hitl_fields[field] = st.text_input(
                    field,
                    value="" if not value else value,
                    key=f"hitl_{field}"
                )

            if st.button("Submit HITL Data"):
                files = {"file": (uploaded_file.name, file_bytes)}
                response = requests.post(
                    "http://127.0.0.1:8000/api/v1/documents/extract",
                    files=files,
                    data={
                        "hitl_name": hitl_fields["name"],
                        "hitl_date_of_birth": hitl_fields["date_of_birth"],
                        "hitl_document_number": hitl_fields["document_number"],
                        "hitl_address": hitl_fields["address"],
                    }
                )

                final_result = response.json()
                st.success("HITL data submitted successfully! Final structured data:")
                st.json(final_result["data"])

        # ------------------- Optional Debug Prompt -------------------
        if st.checkbox("Show raw AI prompt (debug only)"):
            st.subheader("Prompt sent to AI")
            st.code(prompt)