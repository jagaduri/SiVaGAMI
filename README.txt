
SiVaGAMI RAG – Full Code (No Start Scripts)
===========================================
Features:
  - FastAPI backend
  - MongoDB for documents, chat history, feedback/metrics
  - Sentence-Transformers embeddings (all-MiniLM-L6-v2)
  - Retrieval + SSE streaming
  - LLM providers: Ollama (default) OR OpenAI (optional)
  - React + Vite CIBC-style UI (left rail history, upload, center chat, right metrics)

Prereqs:
  - Python 3.10+, Node 18+, MongoDB running (mongod)
  - For local LLM: Ollama =>  ollama serve  &&  ollama pull mistral
  - For OpenAI: export/set OPENAI_API_KEY

Manual Run:
  # 1) Backend
  cd sivagami-rag/backend
  python -m venv .venv
  # Windows: .\.venv\Scripts\activate   |   mac/Linux: source .venv/bin/activate
  pip install --upgrade pip setuptools wheel
  pip install -r requirements.txt
  uvicorn main:app --reload --host 0.0.0.0 --port 8000

  # 2) Frontend (new terminal)
  cd sivagami-rag/frontend
  npm install
  npm run dev

  # Open http://localhost:3000

Notes:
  - Uploads are stored in ./storage and ingested into MongoDB (collection: docs).
  - Supported files: PDF, DOCX, PPTX, XLSX, TXT, MSG, EML.
  - Conversations & messages saved in MongoDB (collections: conversations, messages).
  - Metrics available at GET /metrics (simple running accuracy from /feedback posts).
