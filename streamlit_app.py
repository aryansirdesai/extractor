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

st.title("📄 AI Document Extractor")
st.subheader("Upload Aadhaar, PAN, Passport or any ID document")

# ------------------- Required Fields Selection -------------------
available_fields = [
    "name",
    "date_of_birth",
    "document_number",
    "address",
]

selected_fields = st.multiselect(
    "Select required fields:",
    available_fields,
    default=available_fields
)

# ------------------- File Upload -------------------
uploaded_file = st.file_uploader(
    "Choose a document image (JPEG/PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file and selected_fields:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Document", width=600)

    st.info("Processing document... please wait")
    file_bytes = uploaded_file.getvalue()

    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/documents/extract",
            files={"file": (uploaded_file.name, file_bytes)},
            data={
                "required_fields": ",".join(selected_fields)
            }
        )

        result = response.json()

    except Exception as e:
        st.error(f"Failed to call extraction API: {e}")

    else:
        data = result.get("data", {})
        confidence = result.get("confidence", 0.0)
        hitl_required = result.get("hitl_required", False)

        doc_type = data.get("document_type", "Unknown")

        st.success(f"Document Type: {doc_type}")
        st.info(f"Confidence: {confidence:.2f} | HITL Required: {hitl_required}")

        st.subheader("Extracted Fields")

        for key in selected_fields:
            value = data.get(key)
            if value in [None, "", "MISSING"]:
                st.markdown(
                    f"{key}: <span class='missing-field'>MISSING / INVALID</span>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f"{key}: {value}")

        # ------------------- HITL Section -------------------
        if hitl_required:
            st.warning(
                "Some required fields are missing. Please provide correct values:"
            )

            hitl_fields = {}

            for field in selected_fields:
                raw_value = data.get(field)
                prefill = "" if raw_value in [None, "", "MISSING"] else raw_value

                hitl_fields[field] = st.text_input(
                    field,
                    value=prefill,
                    key=f"hitl_{field}"
                )

            if st.button("Submit HITL Data"):

                response = requests.post(
                    "http://127.0.0.1:8000/api/v1/documents/extract",
                    files={"file": (uploaded_file.name, file_bytes)},
                    data={
                        "required_fields": ",".join(selected_fields),
                        **{f"hitl_{k}": v for k, v in hitl_fields.items()}
                    }
                )

                final_result = response.json()

                st.success("HITL data submitted successfully!")
                st.json(final_result.get("data", {}))