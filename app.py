import streamlit as st
import fitz  # PyMuPDF
import requests
import json
from io import BytesIO
from docx import Document

st.set_page_config(page_title="AI Resume Enhancer", page_icon="📄")

st.title("📄 AI Resume Feedback & Rewriting Tool")

api_key = st.secrets["OPENROUTER_API_KEY"]

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

def extract_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def get_feedback_and_rewrite(resume_text):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
    "model": "mistralai/mistral-7b-instruct",
  # Valid and free
    "messages": [
        {
            "role": "user",
            "content": f"""
Here's a resume:

{resume_text}

Give feedback to improve it and rewrite the resume with professional formatting, tone, and clarity.
"""
        }
    ]
}


    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(body)
    )

    result = response.json()

    # Show raw response in case of error
    if "choices" not in result:
        st.error("⚠️ API did not return expected output. Full response:")
        st.code(json.dumps(result, indent=2))
        raise Exception("Missing 'choices' in response")

    return result['choices'][0]['message']['content']


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
