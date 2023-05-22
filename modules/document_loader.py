import os
import glob
from pypdf import PdfReader

DOCUMENT_DIR = "./documents/"

# handle_loading of pdf files

def load_pdf_text(filename):
    reader = PdfReader(filename)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# create the document loader function
def load_documents(document_dir=DOCUMENT_DIR, file_extensions=['.txt', '.pdf']):
    documents = []
    for file_extension in file_extensions:
        for filename in glob.glob(os.path.join(document_dir, f"*{file_extension}")):
            if file_extension == '.pdf':
                doc_text = load_pdf_text(filename)
            else:
                with open(filename, 'r', encoding="utf-8", errors="replace") as f:
                    doc_text = f.read()
            if doc_text.strip():
                documents.append((doc_text))
            else:
                print(f"Skipping empty document: {filename}")
            return documents