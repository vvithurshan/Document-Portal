from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles                                     
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Any, Optional
from src.document_ingestion.data_ingestion import (
    DocHandler,
    DocumentComparator,
    ChatIngestor,
    FaissManager
)
from src.documentanalyzer.data_analysis import DocumentAnalyzer
from src.documentcomparision.doc_compare import DocumentComparatorLLM
from src.document_chat.retrieval import ConversationalRAG
import os
from pathlib import Path

FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")

app = FastAPI(title = "Document Portal", version = "0.0.1")

# Define project root to resolve static/template paths robustly
PROJECT_ROOT = Path(__file__).resolve().parent.parent

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "static"), name="static")
templates = Jinja2Templates(directory=PROJECT_ROOT / "templates")

@app.get("/", response_class = HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

class FastAPIFileAdapter:
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.filename

    def getbuffer(self) -> bytes:
        self._uf.file.seek(0)
        return self._uf.file.read()

def _read_pdf_via_handler(handler: DocHandler, path: str) -> str:
    if hasattr(handler, "read_pdf"):
        return handler.read_pdf(path)  
    if hasattr(handler, "read_"):
        return handler.read_(path)  
    raise RuntimeError("DocHandler has neither read_pdf nor read_ method.")

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    try:
        dh = DocHandler()
        saved_path = dh.save_pdf(FastAPIFileAdapter(file))
        text = _read_pdf_via_handler(dh, saved_path)
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_document(text)
        return JSONResponse(content = result)

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Analysis failed: {str(e)}")
    
@app.post("/compare")
async def compare_documents(reference: UploadFile = File(...), actual: UploadFile = File(...)) -> Any:
    try:
        dc = DocumentComparator()
        ref_path, act_path = dc.save_uploaded_files(
            FastAPIFileAdapter(reference), 
            FastAPIFileAdapter(actual)
        )
        combined_text = dc.combine_documents()
        comp = DocumentComparatorLLM()
        df = comp.compare_documents(combined_text)
        return {"rows": df.to_dict(orient = "records"),
                "session_id": dc.session_id}
    
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Comparison failed: {str(e)}")
    
@app.post("/chat/index")
async def chat_build_index(files: List[UploadFile] = File(...),
        session_id: Optional[str] = Form(None),
        use_session_dirs: bool = Form(True),
        chunk_size: int = Form(1000),
        chunk_overlap: int = Form(200),
        k: int = Form(5)) -> Any:
    try:
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
            temp_base = UPLOAD_BASE,
            faiss_base = FAISS_BASE,
            use_session_dirs = use_session_dirs,
            session_id = session_id or None
        )
        ci.build_retriver(wrapped, chunk_size = chunk_size, chunk_overlap = chunk_overlap, k = k)
        return {"session_id": ci.session_id,
                "k": k,
                "use_session_dirs": use_session_dirs}
        
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Chat build index failed: {str(e)}")
    
@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5)
) -> Any:
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail = "session_id is required when use_session_dirs = True")
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code = 404, detail = f"FAISS index not found at {index_dir}")
        
        rag = ConversationalRAG(session_id = session_id)
        rag.load_retriever_from_faiss(index_dir)

        response = rag.invoke(question, chat_history=[])
        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG"
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Chat query failed: {str(e)}")
    
# uvicorn api.main:app --port 8080 --reload
# uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
