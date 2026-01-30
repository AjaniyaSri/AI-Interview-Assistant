from pydantic import BaseModel
from typing import List, Optional, Dict

class GenerateRequest(BaseModel):
    role: str
    company: Optional[str] = None
    num_questions: int = 10

class Question(BaseModel):
    type: str  # technical/behavioral/project/general
    question: str

class GenerateResponse(BaseModel):
    questions: List[Question]

class ScoreRequest(BaseModel):
    role: str
    company: Optional[str] = None
    question: str
    answer: str

class ScoreResponse(BaseModel):
    total_score: int
    breakdown: Dict[str, int]
    strengths: List[str]
    improvements: List[str]
    improved_answer: str