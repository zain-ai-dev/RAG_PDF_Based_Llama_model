# backend/app/services/document_processing.py
import uuid
import time
from fastapi import HTTPException  # This is the critical import
from fastapi import UploadFile, BackgroundTasks
from pathlib import Path
import asyncio
from backend.app.services.vector_store_manager import VectorStoreManager
from backend.app.utils.file_utils import save_uploaded_file
from backend.app.core.config import settings

async def process_uploaded_files(background_tasks: BackgroundTasks, files: list[UploadFile]):
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")

        vector_store_manager = VectorStoreManager()
        results = []

        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                continue

            file_id = f"{uuid.uuid4().hex}_{file.filename}"
            try:
                file_path = await save_uploaded_file(file)
                
                vector_store_manager.vector_store_cache[file_id] = {
                    "status": "uploaded",
                    "filename": file.filename,
                    "timestamp": time.time(),
                    "message": "File received, starting processing"
                }
                vector_store_manager._save_statuses()

                background_tasks.add_task(
                    process_single_pdf,
                    file_path,
                    file_id,
                    vector_store_manager
                )

                results.append({
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "processing_started"
                })

            except Exception as e:
                if 'file_path' in locals():
                    try:
                        Path(file_path).unlink(missing_ok=True)
                    except:
                        pass
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process {file.filename}: {str(e)}"
                )

        if not results:
            raise HTTPException(
                status_code=400,
                detail="No valid PDF files were uploaded"
            )

        return {
            "message": "PDFs uploaded successfully",
            "files": results
        }

    except HTTPException:
        raise  # Re-raise FastAPI HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

async def process_single_pdf(file_path: str, file_id: str, vector_store_manager: VectorStoreManager):
    try:
        from backend.app.services.pdf_processor import process_pdf
        
        vector_store_manager.vector_store_cache[file_id].update({
            "status": "processing",
            "message": "Creating vector embeddings",
            "timestamp": time.time()
        })
        vector_store_manager._save_statuses()
        
        # Get FAISS vector store directly
        vector_store = await process_pdf(file_path)
        
        if vector_store is None:
            raise ValueError("Failed to create vector store - no content found")
            
        # Save the vector store
        save_path = settings.VECTOR_STORE_DIR / file_id
        vector_store.save_local(str(save_path))
        
        vector_store_manager.vector_store_cache[file_id].update({
            "status": "done",
            "message": "Processing completed",
            "vector_count": vector_store.index.ntotal,
            "timestamp": time.time()
        })
        vector_store_manager._save_statuses()
        
        # Update active store
        await vector_store_manager._update_active_store()
        
    except Exception as e:
        vector_store_manager.vector_store_cache[file_id].update({
            "status": "failed",
            "message": f"Processing failed: {str(e)}",
            "timestamp": time.time()
        })
        vector_store_manager._save_statuses()
        raise
    finally:
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception as e:
            print(f"Warning: Failed to clean up {file_path}: {str(e)}")