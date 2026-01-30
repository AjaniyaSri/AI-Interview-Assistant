import os
from fastapi import APIRouter
from dotenv import load_dotenv

from app.schemas import GenerateRequest, GenerateResponse, Question
from app.services.vectorstore import get_embedder, get_chroma_client, get_collection, query
from app.services.prompts import QUESTION_PROMPT
from app.services.llm import call_llm

load_dotenv()
router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
def generate_questions(req: GenerateRequest):
    embed_model = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    chroma_dir = os.getenv("CHROMA_DIR", "backend/app/data/chroma_db")

    embedder = get_embedder(embed_model)
    chroma_client = get_chroma_client(chroma_dir)
    collection = get_collection(chroma_client)

    # Pull context from both resume + JD
    resume_hits = query(
        collection, embedder,
        f"{req.role} skills projects experience", k=6,
        source_filter="resume"
    )
    jd_hits = query(
        collection, embedder,
        f"{req.role} requirements responsibilities tech stack", k=6,
        source_filter="jd"
    )

    context = "\n\n".join([h["text"] for h in (resume_hits + jd_hits) if h.get("text")])

    prompt = QUESTION_PROMPT.format(
        role=req.role,
        company=req.company or "N/A",
        context=context[:12000]
    )

    # OpenAI JSON mode: returns a dict like {"questions": [...]}
    out = call_llm(prompt, json_mode=True)

    raw_questions = out.get("questions", [])
    questions: list[Question] = []

    for item in raw_questions:
        if not isinstance(item, dict):
            continue
        q = (item.get("question") or "").strip()
        if not q:
            continue
        questions.append(
            Question(
                type=(item.get("type") or "general").strip(),
                question=q
            )
        )

    # Fallback if model returns nothing
    if not questions:
        questions = [
            Question(
                type="general",
                question=f"Tell me about yourself and why you are a good fit for {req.role}."
            )
        ]

    # Respect requested number, but ensure at least 3 for a decent interview set
    limit = max(3, req.num_questions)
    return GenerateResponse(questions=questions[:limit])