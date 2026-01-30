from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, interview, evaluation, analytics

app = FastAPI(title="AI Interview Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(interview.router, prefix="/interview", tags=["interview"])
app.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

@app.get("/")
def health():
    return {"status": "ok"}