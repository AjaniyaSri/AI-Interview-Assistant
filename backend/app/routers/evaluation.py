import os
import json
from datetime import datetime
from fastapi import APIRouter
from dotenv import load_dotenv

from app.schemas import ScoreRequest, ScoreResponse
from app.services.vectorstore import get_embedder, get_chroma_client, get_collection, query
from app.services.prompts import SCORE_PROMPT
from app.services.llm import call_llm
from app.db import get_conn

load_dotenv()
router = APIRouter()


@router.post("/score", response_model=ScoreResponse)
def score_answer(req: ScoreRequest):
    embed_model = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    chroma_dir = os.getenv("CHROMA_DIR", "backend/app/data/chroma_db")

    embedder = get_embedder(embed_model)
    chroma_client = get_chroma_client(chroma_dir)
    collection = get_collection(chroma_client)

    # Retrieve evidence from resume + JD
    hits = query(collection, embedder, f"{req.question}\n{req.answer}", k=8)
    context = "\n\n".join([
        f"(source={h['meta'].get('source')}, page={h['meta'].get('page')}) {h['text']}"
        for h in hits
        if h.get("text")
    ])[:12000]

    prompt = SCORE_PROMPT.format(
        role=req.role,
        company=req.company or "N/A",
        question=req.question,
        answer=req.answer,
        context=context,
    )

    # OpenAI JSON mode: returns dict
    out = call_llm(prompt, json_mode=True)

    breakdown = out.get("breakdown", {}) if isinstance(out, dict) else {}
    strengths = out.get("strengths", []) if isinstance(out, dict) else []
    improvements = out.get("improvements", []) if isinstance(out, dict) else []
    improved_answer = (out.get("improved_answer", "") if isinstance(out, dict) else "") or ""

    # Ensure breakdown keys exist and are ints
    keys = ["relevance", "clarity", "technical_correctness", "structure", "impact"]
    clean_breakdown = {}
    for k in keys:
        try:
            clean_breakdown[k] = int(breakdown.get(k, 0))
        except Exception:
            clean_breakdown[k] = 0

    total = int(sum(clean_breakdown.values()))

    # Defaults + limit list sizes
    strengths = strengths[:5] if strengths else ["Good effort and relevant direction."]
    improvements = improvements[:5] if improvements else ["Add more concrete examples and measurable impact."]
    improved_answer = improved_answer.strip() or "Try structuring your answer using Situation–Task–Action–Result (STAR)."

    # Store attempt in SQLite
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO attempts(created_at, role, company, question, answer, total_score, breakdown_json)
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            datetime.utcnow().isoformat(),
            req.role,
            req.company or "",
            req.question,
            req.answer,
            total,
            json.dumps(clean_breakdown),
        ),
    )
    conn.commit()

    return ScoreResponse(
        total_score=total,
        breakdown=clean_breakdown,
        strengths=strengths,
        improvements=improvements,
        improved_answer=improved_answer,
    )