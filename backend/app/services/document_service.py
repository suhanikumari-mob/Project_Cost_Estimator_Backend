import tempfile
from langchain_community.document_loaders import Docx2txtLoader



def load_document(requirements_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp1:
            tmp1.write(requirements_bytes)
            file_path = tmp1.name
    except Exception:
        return "Unable to process file into filepath"
    try:
        if file_path.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
            docs = loader.load()
            try:
                file_text = " ".join([page.page_content for page in docs])
                return file_text
            except Exception:
                return "Unable to extract from docs to text"
        else:
            return "Unsupported file"
    except Exception as e:
        return f"File not loaded because {e}"