# backend/app/utils/file_utils.py
import os
import tempfile
from pathlib import Path
from typing import Union
from fastapi import UploadFile

async def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file to temporary location and return path"""
    try:
        # Create temp directory if it doesn't exist
        temp_dir = Path(tempfile.gettempdir()) / "rag_uploads"
        temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Create file path
        file_path = temp_dir / file.filename
        
        # Save file in chunks
        with open(file_path, "wb") as f:
            while content := await file.read(1024 * 1024):  # 1MB chunks
                f.write(content)
        
        return str(file_path)
    
    except Exception as e:
        # Clean up if error occurs
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise RuntimeError(f"Failed to save uploaded file: {str(e)}")