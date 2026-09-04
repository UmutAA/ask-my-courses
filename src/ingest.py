from pathlib import Path
import pdfplumber

def load_pdf(file_name: str, file_path: str = None) -> str:
    """
    Locates the file path and returns content of the PDF
    """

    text_context = ""
    
    if file_path is None:
        parent = Path(__file__).parent
        file_path = parent / "data" / file_name

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content += extracted + " "
            
    except FileNotFoundError:
        print("The file does not exist.")

    return text_context

def chunker(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """
    Creates and returns a list of chunks (strings) with overlap
    """

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap # Advances by leaving an overlap margin
    
    return chunks
