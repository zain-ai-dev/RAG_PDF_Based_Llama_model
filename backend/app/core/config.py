# backend/app/core/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("Missing GROQ API key! Set GROQ_API_KEY in .env file.")
    
    # Constants
    PROCESSING_TIMEOUT = 300
    CACHE_CLEANUP_INTERVAL = 3600
    
    @property
    def VECTOR_STORE_DIR(self) -> Path:
        """Returns the absolute path to vector store directory, creating it if needed"""
        try:
            # Get the project root (RAG_PDF_Based_Llama_model)
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            vector_dir = project_root / "backend" / "static" / "vector_stores"
            
            # Convert to absolute path and create directory
            vector_dir = vector_dir.absolute()
            vector_dir.mkdir(parents=True, exist_ok=True)
            
            # Verify the directory is writable
            test_file = vector_dir / "permission_test.txt"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
            return vector_dir
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize vector store directory at {vector_dir}: {str(e)}\n"
                f"Current working directory: {os.getcwd()}"
            )

    @staticmethod
    def get_tesseract_path():
        if os.name == 'nt':
            return r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        return "/usr/bin/tesseract"
    
    @staticmethod
    def get_poppler_path():
        if os.name == 'nt':
            return r"C:\poppler-24.08.0\Library\bin"
        return "/usr/bin"

settings = Settings()