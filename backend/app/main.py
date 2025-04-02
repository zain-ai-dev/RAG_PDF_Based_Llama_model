# backend/app/main.py
import sys
import os
import contextlib
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import router
from backend.app.core.config import settings
from backend.app.services.vector_store_manager import VectorStoreManager

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    print("Starting application initialization...")
    try:
        # Initialize vector store manager
        print("Creating VectorStoreManager instance...")
        manager = VectorStoreManager()
        print("Initializing VectorStoreManager...")
        await manager.initialize()
        print("Application initialized successfully")
        yield
    except Exception as e:
        print(f"Fatal error during initialization: {str(e)}")
        raise
    
    print("Application shutting down...")

app = FastAPI(
    lifespan=lifespan,
    title="RAG PDF Processor",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )