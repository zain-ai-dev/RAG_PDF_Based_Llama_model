# backend/app/services/pdf_processor.py
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from backend.app.services.ocr_service import extract_text_from_pdf
import os

async def process_pdf(pdf_path: str):
    """Process both text and scanned PDFs"""
    try:
        if not os.path.exists(pdf_path):
            raise ValueError(f"File not found: {pdf_path}")

        # Try regular text extraction first
        try:
            loader = PyMuPDFLoader(pdf_path)
            documents = loader.load()
            
            if documents and any(doc.page_content.strip() for doc in documents):
                print("Text extracted directly from PDF")
            else:
                raise ValueError("No text found in PDF")
                
        except Exception as e:
            print(f"Standard extraction failed, trying OCR: {str(e)}")
            extracted_text = await extract_text_from_pdf(pdf_path)
            if not extracted_text.strip():
                return None
            documents = [Document(page_content=extracted_text)]

        # Split and embed documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(documents)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        return FAISS.from_documents(split_docs, embeddings)

    except Exception as e:
        print(f"PDF processing failed: {str(e)}")
        raise