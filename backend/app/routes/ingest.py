from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil, tempfile, os, hashlib

from app.services.ingestion import ingest_from_url, ingest_from_zip, walk_repo, cleanup
from app.services.parser import parse_all
from app.services.graph import build_graph, graph_summary, graph_to_json
from app.services.chunker import chunk_all
from app.services.vector_store import store_chunks
from app.services.bug_detector import detect_bugs, findings_summary

router = APIRouter()

class RepoURL(BaseModel):
    url: str

@router.post("/ingest/url")
async def ingest_url(payload: RepoURL):
    try:
        repo_path = ingest_from_url(payload.url)
        files = walk_repo(repo_path)
        parsed = parse_all(files)
        G = build_graph(parsed)
        repo_id = hashlib.md5(payload.url.encode()).hexdigest()[:12]
        chunks = chunk_all(parsed)
        num_stored = store_chunks(repo_id, chunks)
        bugs = detect_bugs(parsed)
        result = {
            "repo_id": repo_id,
            "summary": graph_summary(G),
            "graph": graph_to_json(G),
            "chunks_stored": num_stored,
            "bugs": findings_summary(bugs),
        }
        cleanup(repo_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ingest/zip")
async def ingest_zip(file: UploadFile = File(...)):
    tmp_zip = tempfile.mktemp(suffix=".zip")
    try:
        with open(tmp_zip, "wb") as f:
            shutil.copyfileobj(file.file, f)
        repo_path = ingest_from_zip(tmp_zip)
        files = walk_repo(repo_path)
        parsed = parse_all(files)
        G = build_graph(parsed)
        repo_id = hashlib.md5(file.filename.encode()).hexdigest()[:12]
        chunks = chunk_all(parsed)
        num_stored = store_chunks(repo_id, chunks)
        bugs = detect_bugs(parsed)
        result = {
            "repo_id": repo_id,
            "summary": graph_summary(G),
            "graph": graph_to_json(G),
            "chunks_stored": num_stored,
            "bugs": findings_summary(bugs),
        }
        cleanup(repo_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_zip):
            os.remove(tmp_zip)

@router.post("/ingest/debug")
async def ingest_debug(payload: RepoURL):
    repo_path = ingest_from_url(payload.url)
    files = walk_repo(repo_path)
    cleanup(repo_path)
    return {
        "total_files_found": len(files),
        "files": [str(f) for f in files],
    }