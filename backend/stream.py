
import os, json, requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from retriever import retrieve
from models import build_prompt
from config import DEFAULT_PROVIDER, OLLAMA_API, OLLAMA_MODEL_DEFAULT, OPENAI_API_KEY, OPENAI_MODEL_DEFAULT
from conversations import add_message
import multiprocessing

router = APIRouter()

#def stream_ollama(prompt: str, model: str, conv_id: str):
    #payload = {"model": model, "prompt": prompt, "stream": True}
def stream_ollama(prompt: str, model: str, conv_id: str):
    num_threads = max(1, multiprocessing.cpu_count() - 1)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "keep_alive": "5m",
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 256,
            "num_ctx": 2048,
            "num_thread": num_threads
        }
    }
    with requests.post(f"{OLLAMA_API}/api/generate", json=payload, stream=True, timeout=None) as r:
        r.raise_for_status()
        full = ""
        for raw in r.iter_lines(decode_unicode=True):
            if not raw: continue
            try:
                obj = json.loads(raw)
                token = obj.get("token") or obj.get("response") or obj.get("text") or obj.get("content") or ""
            except Exception:
                token = raw
            full += token
            yield f"data: {json.dumps({'token': token})}\n\n"
        if conv_id: add_message(conv_id, "assistant", full)

def stream_openai(prompt: str, model: str, conv_id: str):
    if not OPENAI_API_KEY:
        yield f"event: error\ndata: {json.dumps({'error': 'OPENAI_API_KEY not set'})}\n\n"; return
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    body = {"model": model,"messages":[{"role":"system","content":"You are a helpful assistant."},{"role":"user","content": prompt}],"stream": True,"temperature":0.2}
    with requests.post(url, headers=headers, json=body, stream=True, timeout=None) as r:
        r.raise_for_status()
        full=""
        for raw in r.iter_lines(decode_unicode=True):
            if not raw: continue
            if raw.startswith("data:"):
                data = raw[5:].strip()
                if data == "[DONE]": break
                try:
                    obj = json.loads(data)
                    delta = obj["choices"][0]["delta"].get("content", "")
                    if delta:
                        full += delta
                        yield f"data: {json.dumps({'token': delta})}\n\n"
                except Exception:
                    pass
        if conv_id: add_message(conv_id, "assistant", full)

@router.get("/stream_sse")
def stream_sse(question: str, provider: str = DEFAULT_PROVIDER, model: str = None, k: int = 3, conv_id: str = ""):
    if not question: raise HTTPException(status_code=400, detail="Empty question")
    docs = retrieve(question, k=k); prompt = build_prompt(question, docs)
    if conv_id: add_message(conv_id, "user", question)
    if provider == "openai":
        m = model or OPENAI_MODEL_DEFAULT
        return StreamingResponse(stream_openai(prompt, m, conv_id), media_type="text/event-stream")
    else:
        m = model or OLLAMA_MODEL_DEFAULT
        return StreamingResponse(stream_ollama(prompt, m, conv_id), media_type="text/event-stream")
