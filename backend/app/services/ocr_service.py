# backend/app/services/ocr_service.py
from pathlib import Path 
import pytesseract
from pdf2image import convert_from_path
import fitz
import asyncio
from backend.app.core.config import settings
from typing import List
from io import BytesIO

async def extract_text_from_pdf(pdf_path: str) -> str:
    """More robust OCR with better error messages"""
    try:
        # Verify OCR dependencies
        if not Path(settings.get_tesseract_path()).exists():
            raise RuntimeError(f"Tesseract not found at {settings.get_tesseract_path()}")

        # Convert PDF to images with timeout
        try:
            images = await asyncio.wait_for(
                asyncio.to_thread(
                    convert_from_path,
                    pdf_path,
                    poppler_path=settings.get_poppler_path(),
                    timeout=30  # 30 second timeout
                ),
                timeout=60
            )
        except asyncio.TimeoutError:
            raise RuntimeError("PDF to image conversion timed out")

        # Process images
        texts = []
        for i, img in enumerate(images):
            try:
                text = await asyncio.to_thread(
                    pytesseract.image_to_string,
                    img,
                    timeout=10  # 10 seconds per page
                )
                texts.append(f"--- PAGE {i+1} ---\n{text}")
            except Exception as e:
                texts.append(f"--- PAGE {i+1} OCR FAILED ---\n{str(e)}")
                continue

        return "\n\n".join(texts) if texts else ""

    except Exception as e:
        raise RuntimeError(f"OCR processing failed: {str(e)}")
