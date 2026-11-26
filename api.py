import hashlib
import os
import uuid
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pdf_utils import extract_text_from_files
from qa_engine import AcademicQAEngine

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx"}
FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"

app = FastAPI(title="InquiroAI API")

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS = {}


class QuestionRequest(BaseModel):
    session_id: str
    question: str


def compute_upload_signature(file_records):
    digest = hashlib.sha256()
    for record in file_records:
        digest.update(record["name"].encode("utf-8"))
        digest.update(record["bytes"])
    return digest.hexdigest()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_documents(
    files: list[UploadFile] = File(...),
    session_id: str | None = Form(default=None),
):
    if not files:
        raise HTTPException(status_code=400, detail="Select at least one document to upload.")

    file_records = []
    for upload in files:
        filename = upload.filename or "untitled"
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type for '{filename}'. Upload PDF, DOCX, or PPTX files.",
            )
        raw_bytes = await upload.read()
        file_records.append(
            {
                "name": filename,
                "size": len(raw_bytes),
                "bytes": raw_bytes,
            }
        )

    upload_signature = compute_upload_signature(file_records)
    active_session_id = session_id or uuid.uuid4().hex

    existing_session = SESSIONS.get(active_session_id)
    if existing_session and existing_session["signature"] == upload_signature:
        return {
            "session_id": active_session_id,
            "upload_signature": upload_signature,
            "files": existing_session["files"],
            "file_count": len(existing_session["files"]),
            "unit_count": existing_session["unit_count"],
            "chunk_count": existing_session["chunk_count"],
            "message": "Documents are ready. Ask a question below.",
        }

    wrapped_files = [
        SimpleNamespace(name=record["name"], getvalue=lambda data=record["bytes"]: data)
        for record in file_records
    ]

    try:
        document_units = extract_text_from_files(wrapped_files)
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read uploaded documents: {error}",
        ) from error

    if not document_units:
        raise HTTPException(
            status_code=400,
            detail="No readable text was found in the uploaded documents.",
        )

    try:
        qa_engine = AcademicQAEngine(document_units)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build the search index: {error}",
        ) from error

    file_summaries = [
        {"name": record["name"], "size": record["size"]} for record in file_records
    ]
    SESSIONS[active_session_id] = {
        "signature": upload_signature,
        "engine": qa_engine,
        "files": file_summaries,
        "unit_count": len(document_units),
        "chunk_count": len(qa_engine.chunks),
    }

    return {
        "session_id": active_session_id,
        "upload_signature": upload_signature,
        "files": file_summaries,
        "file_count": len(file_summaries),
        "unit_count": len(document_units),
        "chunk_count": len(qa_engine.chunks),
        "message": "Documents are ready. Ask a question below.",
    }


@app.post("/api/ask")
def ask_question(payload: QuestionRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Enter a question before asking.")

    session = SESSIONS.get(payload.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Document session not found. Upload documents in the sidebar to begin.",
        )

    try:
        result = session["engine"].answer_question(question)
    except (RuntimeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "answer": result["answer"],
        "sources": [
            {"file": file_name, "source": location}
            for file_name, location in result["sources"]
        ],
        "chunks": result["chunks"],
    }


@app.delete("/api/session/{session_id}")
def clear_session(session_id: str):
    SESSIONS.pop(session_id, None)
    return {"status": "cleared"}


if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_react_app(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        target = FRONTEND_DIST / full_path
        if full_path and target.is_file():
            return FileResponse(target)
        return FileResponse(FRONTEND_DIST / "index.html")
