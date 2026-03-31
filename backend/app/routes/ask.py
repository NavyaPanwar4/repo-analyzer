from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.vector_store import query_chunks
from app.services.llm import ask_llm, summarise_bugs

router = APIRouter()

class AskPayload(BaseModel):
    repo_id: str
    question: str
    summary: dict = None

class BugSummaryPayload(BaseModel):
    findings: list

@router.post("/ask")
async def ask_question(payload: AskPayload):
    try:
        hits = query_chunks(payload.repo_id, payload.question)
        answer = ask_llm(payload.question, hits, summary=payload.summary)
        return {
            "question": payload.question,
            "answer": answer,
            "context_chunks": hits,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bugs/explain")
async def explain_bugs(payload: BugSummaryPayload):
    try:
        explanation = summarise_bugs(payload.findings)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))