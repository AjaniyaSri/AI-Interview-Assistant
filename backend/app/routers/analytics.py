import json
from fastapi import APIRouter
from app.db import get_conn

router = APIRouter()

@router.get("/history")
def history(limit: int = 50):
    conn = get_conn()
    cur = conn.execute(
        "SELECT created_at, role, company, question, total_score, breakdown_json FROM attempts ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    out = []
    for r in rows:
        out.append({
            "created_at": r[0],
            "role": r[1],
            "company": r[2],
            "question": r[3],
            "total_score": r[4],
            "breakdown": json.loads(r[5] or "{}"),
        })
    return {"items": out}

@router.get("/summary")
def summary():
    conn = get_conn()
    cur = conn.execute("SELECT COUNT(*), AVG(total_score) FROM attempts")
    count, avg = cur.fetchone()
    return {"attempts": int(count or 0), "avg_score": float(avg or 0.0)}