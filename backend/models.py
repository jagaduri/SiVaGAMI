
import os, json, requests
from config import DEFAULT_PROVIDER, OLLAMA_API, OLLAMA_MODEL_DEFAULT, OPENAI_API_KEY, OPENAI_MODEL_DEFAULT
import os, json, requests, multiprocessing
from config import OLLAMA_API

def build_prompt(question: str, docs: list) -> str:
    context = "\n\n".join([f"Filename: {d['filename']}\n{d['content']}" for d in docs])
    return f"Context:\n{context}\n\nQuestion: {question}\nAnswer concisely and cite the filenames used."

def call_ollama(prompt: str, model: str):
    num_threads = max(1, multiprocessing.cpu_count() - 1)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "5m",
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 256,     # cap the answer length
            "num_ctx": 2048,        # context window
            "num_thread": num_threads
        }
    }
    r = requests.post(f"{OLLAMA_API}/api/generate", json=payload, timeout=120)

def call_openai(prompt: str, model: str):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    body = {"model": model,"messages":[{"role":"system","content":"You are a helpful assistant."},{"role":"user","content": prompt}],"temperature":0.2,"stream":False}
    r = requests.post(url, headers=headers, json=body, timeout=120)
    try: return r.json()["choices"][0]["message"]["content"]
    except Exception: return f"OpenAI error: {r.text}"

def generate_answer(question: str, docs: list, provider: str=None, model: str=None):
    provider = (provider or DEFAULT_PROVIDER).lower()
    if provider not in ("ollama","openai"): provider="ollama"
    prompt = build_prompt(question, docs)
    if provider=="ollama":
        return call_ollama(prompt, model or OLLAMA_MODEL_DEFAULT)
    else:
        if not os.getenv("OPENAI_API_KEY"): return "OPENAI_API_KEY not set."
        return call_openai(prompt, model or OPENAI_MODEL_DEFAULT)
