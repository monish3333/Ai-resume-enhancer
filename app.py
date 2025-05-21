import streamlit as st
import fitz  # PyMuPDF
import openai

st.set_page_config(page_title="AI Resume Reviewer")

st.title("📄 AI Resume Feedback Tool")

openai.api_key = st.text_input("Enter your OpenAI API key", type="password")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

def extract_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def get_feedback_and_rewrite(resume_text):
    prompt = f"""
    Here's a resume:
    {resume_text}

    1. Give professional feedback to improve it.
    2. Rewrite the resume with improved formatting, tone, and clarity.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

if uploaded_file and openai.api_key:
    text = extract_text(uploaded_file)
    if st.button("Analyze Resume"):
        with st.spinner("Processing..."):
            result = get_feedback_and_rewrite(text)
        st.text_area("✍️ AI Feedback & Improved Resume", result, height=500)
