import os
import uuid
from fastapi import APIRouter, UploadFile, File
from dotenv import load_dotenv

from app.services.parsing import pdf_to_text
from app.services.vectorstore import get_embedder, get_chroma_client, get_collection, upsert_document

load_dotenv()
router = APIRouter()

@router.post("/{doc_type}")
async def upload_doc(doc_type: str, file: UploadFile = File(...)):
    if doc_type not in ["resume", "jd"]:
        return {"error": "doc_type must be resume or jd"}

    data_dir = os.getenv("DATA_DIR", "backend/app/data")
    uploads_dir = os.path.join(data_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    doc_id = str(uuid.uuid4())
    file_path = os.path.join(uploads_dir, f"{doc_id}_{doc_type}.pdf")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    pages = pdf_to_text(file_path)

    embed_model = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    chroma_dir = os.getenv("CHROMA_DIR", "backend/app/data/chroma_db")

    embedder = get_embedder(embed_model)
    client = get_chroma_client(chroma_dir)
    collection = get_collection(client)

    upsert_document(collection, embedder, doc_type=doc_type, pages=pages, doc_id=doc_id)

    return {"status": "uploaded", "doc_type": doc_type, "doc_id": doc_id, "pages": len(pages)}