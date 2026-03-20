import streamlit as st
import os
import io
import platform
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pytesseract
from groq import Groq

# --- 1. SETUP ---
load_dotenv()
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- 2. SMART EXTRACTION ---
def extract_text(file):
    """Template ya Evidence se text nikalne ke liye"""
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.name.lower().endswith(".docx"):
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    else: # Images/Screenshots
        img = Image.open(file)
        return pytesseract.image_to_string(img)

def generate_smart_report(template_style, evidence_content, api_key):
    """AI logic: Style matching + Analysis"""
    temp_client = Groq(api_key=api_key)
    
    # AI ko sakht instruction ke template ka style copy kare
    prompt = f"""
    TASK: Generate a professional Cyber Security Pentest Report.
    
    1. STYLE REFERENCE (Follow this template's tone and structure):
    {template_style[:1000]} 
    
    2. EVIDENCE DATA (Analyze these screenshots/files):
    {evidence_content}
    
    INSTRUCTIONS:
    - Identify vulnerabilities from the evidence.
    - Write summaries, risk levels (High/Med/Low), and technical suggestions.
    - Match the 'tarteeb' and professional language of the template.
    - Output only the report content.
    """
    
    try:
        response = temp_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are an expert Pentester. Format your response exactly like the provided template style."},
                      {"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analysis Failed: {e}"

# --- 3. UI ---
st.set_page_config(page_title="AI Report Architect", layout="wide")
st.title("🛡️ CyberReport AI: Smart Template Matcher")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 1. Upload Template Style")
    template_input = st.file_uploader("Upload Sample (PDF/Word)", type=["pdf", "docx"])

with col2:
    st.subheader("📸 2. Upload Evidence")
    evidence_inputs = st.file_uploader("Upload Screenshots/Logs", type=["png", "jpg", "jpeg", "pdf", "docx"], accept_multiple_files=True)

# --- 4. EXECUTION ---
if st.button("🚀 Analyze & Generate Report"):
    if template_input and evidence_inputs and GROQ_API_KEY:
        with st.spinner("AI is studying your template and analyzing evidence..."):
            
            # Step A: Template ka style samjhna
            style_guide = extract_text(template_input)
            
            # Step B: Saare screenshots/files ko analyze karna
            evidence_data = ""
            for f in evidence_inputs:
                evidence_data += f"\n--- File: {f.name} ---\n" + extract_text(f)
            
            # Step C: AI Report Generation
            final_content = generate_smart_report(style_guide, evidence_data, GROQ_API_KEY)
            
            st.success("✅ Analysis Complete!")
            st.markdown(final_content) # Preview
            
            # Step D: Export as Word (Default for editing)
            new_doc = Document()
            new_doc.add_paragraph(final_content)
            doc_io = io.BytesIO()
            new_doc.save(doc_io)
            doc_io.seek(0)
            
            st.download_button(label="📥 Download as Word (.docx)", 
                               data=doc_io, 
                               file_name="AI_Generated_Report.docx")
    else:
        st.error("Please provide both Template and Evidence.")
