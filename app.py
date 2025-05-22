import streamlit as st
import fitz  # PyMuPDF
import requests
import json
from io import BytesIO
from docx import Document

st.set_page_config(page_title="AI Resume Enhancer", page_icon="📄")
st.title("📄 AI Resume Feedback & Rewriting Tool")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

def extract_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

import requests
import json

def get_feedback_and_rewrite(resume_text):
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "model": "tinyllama_-_tinyllama-1.1b-chat-v1.0",  # ✅ your exact model ID
        "messages": [
            {
                "role": "user",
                "content": f"""
Here's a resume:

{resume_text}

Give feedback to improve it and rewrite it with professional formatting, tone, and clarity.
"""
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "http://192.168.137.135:1234/v1/chat/completions",  # ✅ your local LM Studio server
            headers=headers,
            data=json.dumps(body)
        )
        result = response.json()

        if "choices" not in result:
            st.error("⚠️ LM Studio returned an unexpected response:")
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
