# 🛡️ CyberReport AI Pro (Pentest Automator)

**CyberReport AI Pro** ek advanced tool hai jo Cyber Security professionals ke liye reporting ke mushkil kaam ko asaan banata hai. Ye tool AI (Llama 3.3) aur OCR technology ko use karte hue screenshots aur raw logs se findings nikal kar direct aapke professional templates mein fill kar deta hai.

## 🚀 Features
- **Smart Evidence Extraction:** PDFs aur Screenshots (Images) se automatically text extract karta hai (Tesseract OCR).
- **AI-Powered Analysis:** Groq Cloud aur Llama 3.3 use karte hue raw data ko professional OWASP-standard findings mein badalta hai.
- **Template Mapping:** Aapke custom `.docx` templates ke saath integrate hota hai (Bas `{{RESULT}}` tag use karein).
- **Scalable & Fast:** Caching aur Batching features ke saath fast processing.
- **Secure:** Environment variables aur Streamlit Secrets support.

## 🛠️ Tech Stack
- **Language:** Python
- **Interface:** Streamlit (Minimalist & Stable)
- **AI Model:** Llama 3.3-70b (via Groq)
- **OCR:** Tesseract OCR
- **Document Handling:** Python-Docx & PyPDF2

## 📦 Installation & Setup
Agar aap isse locally chalana chahte hain:

1. Clone the repo:
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
