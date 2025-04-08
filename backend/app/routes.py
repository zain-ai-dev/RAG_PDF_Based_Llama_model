# backend/app/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from backend.app.services.document_processing import process_uploaded_files  # Changed from relative to absolute
from backend.app.services.query_service import handle_query
from backend.app.models.schemas import QueryRequest
from backend.app.services.vector_store_manager import VectorStoreManager

router = APIRouter()

@router.post("/upload/")
async def upload_pdfs(
    background_tasks: BackgroundTasks, 
    files: list[UploadFile] = File(...)
):
    try:
        return await process_uploaded_files(background_tasks, files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/")
async def query_pdfs(request: QueryRequest):
    try:
        response = await handle_query(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{file_id}")
async def check_status(file_id: str):
    try:
        vector_store_manager = VectorStoreManager()
        status_info = vector_store_manager.get_file_status(file_id)
        
        if not status_info:
            # Check if file exists in storage
            store_path = settings.VECTOR_STORE_DIR / file_id
            if store_path.exists():
                return {
                    "file_id": file_id,
                    "status": "done",
                    "message": "File was processed but status not tracked",
                    "timestamp": store_path.stat().st_mtime
                }
            raise HTTPException(status_code=404, detail="File ID not found")
        
        return status_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    