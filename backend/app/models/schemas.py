# backend/app/models/schemas.py
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class FileStatus(BaseModel):
    file_id: str
    filename: str
    status: str
    message: str = ""
    timestamp: float

class QueryResponse(BaseModel):
    response: str
    sources: list[dict]