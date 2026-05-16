from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Add this
from fastapi.responses import FileResponse # Add this
from pydantic import BaseModel
import shutil
import os
import uuid
from typing import List, Dict
from langchain_core.messages import HumanMessage, AIMessage 

from app.core.engine import RAGEngine
from app.services.pdf_loader import PDFProcessor

app = FastAPI(title="Omni-RAG Engine", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
rag_engine = RAGEngine()
pdf_processor = PDFProcessor()
TEMP_DIR = "app/temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- NEW: Serve the Frontend ---

# 1. Mount the static directory (for JS/CSS/Images)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the index.html file at the root URL"""
    return FileResponse("app/static/index.html")

# --- End of Frontend Routes ---

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = [] # Expect a list of role/content pairs

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(TEMP_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        chunks = pdf_processor.process_pdf(file_path)
        rag_engine.ingest_pdf(chunks)
        
        return {"message": "Success", "filename": file.filename, "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/chat")
async def chat_with_doc(request: ChatRequest):
    try:
        formatted_history = []
        # Ensure request.history is not None and is a list
        if request.history:
            for msg in request.history:
                role = msg.get("role")
                content = msg.get("content")
                if content and role == "user":
                    formatted_history.append(HumanMessage(content=content))
                elif content and role == "assistant":
                    formatted_history.append(AIMessage(content=content))

        answer = rag_engine.get_answer(request.query, formatted_history)
        return {"answer": answer}
    except Exception as e:
        print(f"BACKEND ERROR: {str(e)}") # Keep this for debugging!
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


