# backend/app/services/vector_store_manager.py
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from backend.app.core.config import settings

class VectorStoreManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize all required attributes"""
        self.status_file = settings.VECTOR_STORE_DIR / "processing_status.json"
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        settings.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        self.vector_store_cache = {}
        self.active_vector_store = None
        self._load_statuses()  # Load existing statuses

    def _load_statuses(self):
        """Load processing statuses from file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    self.vector_store_cache = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load statuses: {str(e)}")
            self.vector_store_cache = {}

    def _save_statuses(self):
        """Save current statuses to file"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self.vector_store_cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save statuses: {str(e)}")

    async def initialize(self):
        """Complete initialization including async tasks"""
        await self._initialize_active_store()
        self.cleanup_old_entries()
        print("VectorStoreManager initialized successfully")

    async def _initialize_active_store(self):
        """Initialize active store from existing vector stores"""
        try:
            processed_dirs = [d for d in settings.VECTOR_STORE_DIR.iterdir() 
                            if d.is_dir() and not d.name.endswith('.json')]
            
            for store_dir in processed_dirs:
                file_id = store_dir.name
                if file_id not in self.vector_store_cache:
                    self.vector_store_cache[file_id] = {
                        "status": "done",
                        "filename": file_id.split('_', 1)[-1],
                        "timestamp": store_dir.stat().st_mtime,
                        "message": "Discovered existing vector store"
                    }
            
            await self._update_active_store()
            self._save_statuses()
        except Exception as e:
            print(f"Warning: Failed to initialize active store: {str(e)}")

    def get_file_status(self, file_id: str) -> Dict:
        """Get processing status with fallback to physical store check"""
        status = self.vector_store_cache.get(file_id, {})
        
        if not status and (settings.VECTOR_STORE_DIR / file_id).exists():
            return {
                "file_id": file_id,
                "status": "done",
                "message": "File was processed but status not tracked",
                "timestamp": (settings.VECTOR_STORE_DIR / file_id).stat().st_mtime
            }
        return status

    async def add_documents(self, file_id: str, documents: List, metadata: Dict):
        """Add documents to the vector store with comprehensive tracking"""
        if not documents or not isinstance(documents, list):
            raise ValueError("Valid documents list required")
        
        try:
            # Initialize status tracking
            self.vector_store_cache[file_id] = {
                "status": "processing",
                "filename": metadata.get("filename", file_id.split('_', 1)[-1]),
                "timestamp": time.time(),
                "message": "Starting document processing"
            }
            self._save_statuses()
            
            # Create and save vector store
            self.vector_store_cache[file_id]["message"] = "Creating embeddings"
            vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            save_path = settings.VECTOR_STORE_DIR / file_id
            save_path.mkdir(exist_ok=True)
            vector_store.save_local(str(save_path))
            
            # Update status
            self.vector_store_cache[file_id].update({
                "status": "done",
                "message": "Processing completed",
                "vector_count": vector_store.index.ntotal,
                "timestamp": time.time()
            })
            self._save_statuses()
            
            # Update active store
            await self._update_active_store()
            
        except Exception as e:
            if file_id in self.vector_store_cache:
                self.vector_store_cache[file_id].update({
                    "status": "failed",
                    "message": f"Error: {str(e)}",
                    "timestamp": time.time()
                })
                self._save_statuses()
            raise

    async def _update_active_store(self):
        """Rebuild the active vector store from processed files"""
        processed_files = [
            file_id for file_id, data in self.vector_store_cache.items()
            if data.get("status") == "done"
            and (settings.VECTOR_STORE_DIR / file_id).exists()
        ]
        
        self.active_vector_store = None
        
        for file_id in processed_files:
            try:
                vector_store = FAISS.load_local(
                    str(settings.VECTOR_STORE_DIR / file_id),
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True
                )
                
                if self.active_vector_store is None:
                    self.active_vector_store = vector_store
                else:
                    self.active_vector_store.merge_from(vector_store)
                    
            except Exception as e:
                print(f"Warning: Could not load {file_id}: {str(e)}")
                continue

    def get_active_store(self) -> Optional[FAISS]:
        """Get the current active vector store"""
        return self.active_vector_store

    def cleanup_old_entries(self, max_age_hours: int = 24):
        """Clean up old entries with logging"""
        cutoff = time.time() - (max_age_hours * 3600)
        cleaned = 0
        
        for file_id, data in list(self.vector_store_cache.items()):
            if data.get("timestamp", 0) < cutoff:
                try:
                    store_path = settings.VECTOR_STORE_DIR / file_id
                    if store_path.exists():
                        for f in store_path.glob("*"):
                            f.unlink(missing_ok=True)
                        store_path.rmdir()
                    self.vector_store_cache.pop(file_id, None)
                    cleaned += 1
                except Exception as e:
                    print(f"Warning: Failed to clean up {file_id}: {str(e)}")
        
        if cleaned:
            print(f"Cleaned up {cleaned} old vector stores")
        self._save_statuses()