import streamlit as st
import fitz  # PyMuPDF
import requests
import json
from io import BytesIO
from docx import Document

st.set_page_config(page_title="AI Resume Enhancer", page_icon="📄")

st.title("📄 AI Resume Feedback & Rewriting Tool")

api_key = "lm-studio"  # dummy value for local use

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

def extract_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])


openai.api_key = "lm-studio"
openai.api_base = "http://127.0.0.1:1234/v1"  # your local LM Studio server

def get_feedback_and_rewrite(resume_text):
    prompt = f"""
Here's a resume:

{resume_text}

Give professional feedback to improve this resume. Then rewrite it with better formatting, tone, and clarity.
"""

    headers = {"Content-Type": "application/json"}
    
    body = {
        "model": "local-model",  # or use actual name from LM Studio
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "http://127.0.0.1:1234/v1/chat/completions",
            headers=headers,
            data=json.dumps(body)
        )
        result = response.json()

        if "choices" not in result:
            st.error("⚠️ Unexpected response from LM Studio:")
            st.code(json.dumps(result, indent=2))
            return "Error: No output received from the model."

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        st.error("❌ Failed to connect to LM Studio.")
        st.code(str(e))
        return "Error: Failed to connect to local AI model."


def generate_docx(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

if uploaded_file:
    if st.button("Analyze Resume"):
        with st.spinner("Thinking..."):
            resume_text = extract_text(uploaded_file)
            try:
                output = get_feedback_and_rewrite(resume_text)
                st.text_area("🧠 AI Feedback & Rewritten Resume", output, height=500)

                # Download as TXT
                st.download_button(
                    label="⬇️ Download as TXT",
                    data=output,
                    file_name="improved_resume.txt",
                    mime="text/plain"
                )

                # Download as DOCX
                docx_file = generate_docx(output)
                st.download_button(
                    label="⬇️ Download as DOCX",
                    data=docx_file,
                    file_name="improved_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            except Exception as e:
                st.error(f"❌ Error: {e}")
