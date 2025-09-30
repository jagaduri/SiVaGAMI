
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os, traceback
from ingestion import ingest_file
from retriever import retrieve
from models import generate_answer
from feedback import save_feedback, get_metrics
from conversations import start_conversation, list_conversations, get_messages, add_message, rename_conversation, delete_conversation
from stream import router as stream_router

app = FastAPI(title="SiVaGAMI RAG (Full, No Scripts)")

origins = ["http://localhost:3000","http://127.0.0.1:3000","http://localhost:5173"]
app.add_middleware(CORSMiddleware, allow_origins=origins+["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(stream_router)

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    os.makedirs("storage", exist_ok=True)
    results=[]
    for f in files:
        p = f"storage/{f.filename}"
        with open(p, "wb") as out:
            out.write(await f.read())
        num = ingest_file(p)
        results.append({"filename": f.filename, "chunks": num})
    return {"status":"ok","ingested":results}

@app.post("/chat")
async def chat(payload: dict):
    try:
        q = payload.get("question","")
        provider = payload.get("provider"); model = payload.get("model")
        conv_id = payload.get("conv_id","")
        if not q: raise HTTPException(status_code=400, detail="Empty question")
        docs = retrieve(q, k=3)
        if conv_id: add_message(conv_id, "user", q)
        ans = generate_answer(q, docs, provider=provider, model=model)
        if conv_id: add_message(conv_id, "assistant", ans)
        return {"answer": ans, "docs": docs, "conv_id": conv_id}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Conversations
@app.post("/conversations/start")
def conversations_start(payload: dict = {}):
    title = payload.get("title","New chat")
    cid = start_conversation(title)
    return {"conv_id": cid, "title": title}

@app.get("/conversations")
def conversations_list():
    return list_conversations()

@app.get("/conversations/{conv_id}/messages")
def conversations_messages(conv_id: str):
    return get_messages(conv_id)

@app.post("/conversations/{conv_id}/rename")
def conversations_rename(conv_id: str, payload: dict):
    rename_conversation(conv_id, payload.get("title","Untitled"))
    return {"status":"ok"}

@app.post("/feedback")
async def feedback(payload: dict):
    save_feedback(payload); return {"status":"saved"}

@app.get("/metrics")
async def metrics(): return get_metrics()

@app.get("/debug/health")
def debug_health():
    try:
        from pymongo import MongoClient
        from config import MONGO_URI, DB_NAME
        c = MongoClient(MONGO_URI); db = c[DB_NAME]
        return {"ok": True, "docs_count": db["docs"].count_documents({}), "convs": db["conversations"].count_documents({})}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    
@app.post("/conversations/{conv_id}/rename")
def conversations_rename(conv_id: str, payload: dict):
    rename_conversation(conv_id, payload.get("title","Untitled"))
    return {"status":"ok"}

@app.delete("/conversations/{conv_id}")
def conversations_delete(conv_id: str):
    delete_conversation(conv_id)
    return {"status":"deleted"}
