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

# --- 1. SECURITY & PATH FIX ---
load_dotenv()
# Streamlit Cloud ke Secrets se key uthayega, agar wahan na ho to .env se
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

# Tesseract Path Fix (Automated)
if platform.system() == "Windows":
    # Agar aap apne laptop par chala rahi hain
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    # Linux/Cloud par path dene ki zaroorat nahi hoti, bas command chalti hai
    pass

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- 2. LOGIC: Caching & OCR ---
@st.cache_data(show_spinner=False)
def get_text_from_files(file_list):
    all_text = ""
    for file in file_list:
        try:
            if file.type == "application/pdf":
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    all_text += page.extract_text() + "\n"
            else:
                img = Image.open(file)
                # Image ko scan kar raha hai
                ocr_text = pytesseract.image_to_string(img)
                all_text += f"\n[Evidence: {file.name}]\n{ocr_text}\n"
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
    return all_text

def process_with_ai_batched(prompt_text, api_key_to_use):
    # Dynamic client for users who enter key manually
    temp_client = Groq(api_key=api_key_to_use)
    try:
        response = temp_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a Cyber Security Expert. Summarize evidence into professional pentest findings (OWASP focus)."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Failed: {str(e)}"

def fill_template(template_file, findings):
    doc = Document(template_file)
    # Template mein {{RESULT}} ko findings se badal dega
    for p in doc.paragraphs:
        if "{{RESULT}}" in p.text:
            p.text = p.text.replace("{{RESULT}}", findings)
    
    # Save to memory buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. UI SETUP (Minimalist & Stable) ---
st.set_page_config(page_title="CyberReport AI Pro", page_icon="🛡️")

st.title("🛡️ Cyber Pentest Report AI (Pro)")
st.markdown("---")

# Sidebar for Key
with st.sidebar:
    st.header("⚙️ Configuration")
    user_api_key = st.text_input("Enter Groq API Key", type="password", value=GROQ_API_KEY if GROQ_API_KEY else "")
    st.info("Note: Your template must contain the tag: **{{RESULT}}**")

# Layout Columns
col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 Template")
    template_file = st.file_uploader("Upload .docx", type=["docx"])
with col2:
    st.subheader("📸 Evidence")
    evidence_files = st.file_uploader("Upload PDF/Images", type=["pdf", "png", "jpg"], accept_multiple_files=True)

# --- 4. EXECUTION ---
if st.button("🚀 Generate Professional Report"):
    if template_file and evidence_files and user_api_key:
        with st.spinner("Processing Evidence & AI Analysis..."):
            # Step A: Data Extraction
            full_data = get_text_from_files(evidence_files)
            
            # Step B: AI Logic
            ai_findings = process_with_ai_batched(full_data, user_api_key)
            
            # Step C: Template Mapping
            final_report = fill_template(template_file, ai_findings)
            
            st.success("✅ Report Generated!")
            
            # Download Button
            st.download_button(
                label="📥 Download Final Report",
                data=final_report,
                file_name="AI_Pentest_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            with st.expander("Preview Findings"):
                st.write(ai_findings)
    else:
        st.warning("Please ensure Template, Evidence, and API Key are provided.")