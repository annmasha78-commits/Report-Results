import streamlit as st
import os
import io
import platform
from datetime import datetime
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

def extract_text(file):
    """File se text nikalne ka function"""
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.name.lower().endswith(".docx"):
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    else: # Images/OCR
        img = Image.open(file)
        return pytesseract.image_to_string(img)

# --- 2. UI SETUP ---
st.set_page_config(page_title="CyberReport AI Pro", page_icon="🛡️", layout="wide")

with st.sidebar:
    st.header("⚙️ Configuration")
    user_api_key = st.text_input("Enter Groq API Key", type="password", value=GROQ_API_KEY if GROQ_API_KEY else "")
    
    # Naya Feature: Manual Instructions
    st.subheader("✍️ Custom Hidayat (Optional)")
    custom_instructions = st.text_area("AI ko batayein report kaisi honi chahiye:", 
                                     placeholder="e.g. Report ko points mein rakho aur technical terms zyada use karo...")
    
    st.divider()
    st.info(f"Report Date: {datetime.now().strftime('%d-%m-%Y')}")

st.title("🛡️ Cyber Pentest Report AI (Ultimate)")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 1. Report Template/Pattern")
    template_input = st.file_uploader("Upload Sample (Pattern Reference)", type=["docx", "pdf"], key="tpl")

with col2:
    st.subheader("📸 2. Evidence & Data")
    evidence_inputs = st.file_uploader("Upload Screenshots/PDFs/Logs", 
                                     type=["png", "jpg", "jpeg", "pdf", "docx"], 
                                     accept_multiple_files=True, key="evd")

# --- 3. EXECUTION ---
if st.button("🚀 Analyze & Generate Final Report"):
    if not user_api_key:
        st.error("Sidebar mein API Key dalein!")
    elif not template_input or not evidence_inputs:
        st.error("Template aur Evidence dono upload karna zaroori hai.")
    else:
        with st.spinner("AI aapki hidayat aur evidence ka tajziya kar raha hai..."):
            try:
                # Aaj ki date
                report_date = datetime.now().strftime("%B %d, %Y")
                
                # Data Extraction
                style_pattern = extract_text(template_input)
                evidence_data = ""
                for f in evidence_inputs:
                    evidence_data += f"\n[SOURCE_FILE: {f.name}]\n" + extract_text(f)
                
                # Smart AI Prompt
                temp_client = Groq(api_key=user_api_key)
                full_prompt = f"""
                CURRENT DATE: {report_date}
                
                PATTERN REFERENCE (Sirf structure follow karein, purana data ignore karein):
                {style_pattern[:1500]}
                
                EVIDENCE DATA (Inko analyze karke vulnerabilities nikalein):
                {evidence_data}
                
                SPECIAL INSTRUCTIONS FROM USER:
                {custom_instructions if custom_instructions else "Professional pentest report banayein."}
                
                TASK:
                1. Report ka pattern template jaisa ho lekin content sirf evidence se ho.
                2. Purani dates ya logos remove karke '{report_date}' likhein.
                3. Jahan screenshot zaroori ho, wahan placeholder dalein: '[INSERT SCREENSHOT: filename]'.
                4. Technical accuracy ka khayal rakhein.
                """
                
                response = temp_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are an Elite Cyber Security Expert."},
                              {"role": "user", "content": full_prompt}],
                    temperature=0.2
                )
                
                final_report_text = response.choices[0].message.content
                
                st.success("✅ Report Tayyar Hai!")
                st.markdown(final_report_text)
                
                # Word File Download logic
                new_doc = Document()
                new_doc.add_heading(f"Pentest Report - {report_date}", 0)
                new_doc.add_paragraph(final_report_text)
                
                doc_io = io.BytesIO()
                new_doc.save(doc_io)
                doc_io.seek(0)
                
                st.download_button("📥 Download Final Word Report", 
                                   data=doc_io, 
                                   file_name=f"Pentest_Report_{datetime.now().strftime('%Y%m%d')}.docx")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
