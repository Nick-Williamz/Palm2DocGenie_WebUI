import os
import glob

DOCUMENT_DIR = "./documents/"

def load_documents(document_dir=DOCUMENT_DIR):
    documents = []
    for filename in glob.glob(os.path.join(document_dir, "*.txt")):
        with open(filename, 'r', encoding='utf-8') as file:
            doc_text = file.read()
            if doc_text.strip():
                print(f"Loaded document '{filename}' with length {len(doc_text)}:\n{doc_text}\n")
                documents.append(doc_text)
            else:
                print(f"Skipped empty document '{filename}'")
    return documents