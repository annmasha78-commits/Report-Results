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

# --- 1. SETUP & SECURITY ---
load_dotenv()
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- 2. EXTRACTION LOGIC ---
def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.name.lower().endswith(".docx"):
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    else: # Images/OCR
        img = Image.open(file)
        return pytesseract.image_to_string(img)

# --- 3. UI SETUP (Wapis Sidebar ke Saath) ---
st.set_page_config(page_title="CyberReport AI Pro", page_icon="🛡️", layout="wide")

# SIDEBAR (Aapka Purana Feature)
with st.sidebar:
    st.header("⚙️ Configuration")
    # API Key box wapis aa gaya
    user_api_key = st.text_input("Enter Groq API Key", type="password", value=GROQ_API_KEY if GROQ_API_KEY else "")
    st.divider()
    st.info("Template Upload karein (Style ke liye) aur Evidence (Analysis ke liye).")

st.title("🛡️ Cyber Pentest Report AI (Pro)")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 1. Report Template")
    template_input = st.file_uploader("Upload Sample (Word/PDF)", type=["docx", "pdf"], key="tpl")

with col2:
    st.subheader("📸 2. Evidence & Data")
    evidence_inputs = st.file_uploader("Upload Screenshots/PDFs/Logs", type=["png", "jpg", "jpeg", "pdf", "docx"], accept_multiple_files=True, key="evd")

# --- 4. EXECUTION ---
if st.button("🚀 Analyze Evidence & Generate Report"):
    # Check karein ke sab kuch provide kiya gaya hai
    if not user_api_key:
        st.error("Please enter your Groq API Key in the sidebar!")
    elif not template_input:
        st.error("Please upload a Template file.")
    elif not evidence_inputs:
        st.error("Please upload at least one Evidence file.")
    else:
        with st.spinner("AI is analyzing evidence based on your template..."):
            try:
                # A. Template ka style extract karna
                style_guide = extract_text(template_input)
                
                # B. Evidence se data nikalna
                evidence_data = ""
                for f in evidence_inputs:
                    evidence_data += f"\n--- Source: {f.name} ---\n" + extract_text(f)
                
                # C. AI Analysis (Smart Style Matching)
                temp_client = Groq(api_key=user_api_key)
                prompt = f"TEMPLATE STYLE:\n{style_guide[:1000]}\n\nEVIDENCE:\n{evidence_data}\n\nTASK: Analyze evidence and write a report in the EXACT style of the template above."
                
                response = temp_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are a professional Pentester."},
                              {"role": "user", "content": prompt}],
                    temperature=0.2
                )
                
                final_content = response.choices[0].message.content
                
                st.success("✅ Report Generated!")
                st.markdown(final_content)
                
                # Word File Download
                new_doc = Document()
                new_doc.add_paragraph(final_content)
                doc_io = io.BytesIO()
                new_doc.save(doc_io)
                doc_io.seek(0)
                
                st.download_button("📥 Download Final Report (.docx)", data=doc_io, file_name="Pentest_Report.docx")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
