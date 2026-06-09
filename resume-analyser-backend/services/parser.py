import pdfplumber
import docx
import io

def extract_text(content: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif "wordprocessingml" in content_type:
        doc = docx.Document(io.BytesIO(content))
        return "\n".join(para.text for para in doc.paragraphs)
    raise ValueError("Unsupported file type")
