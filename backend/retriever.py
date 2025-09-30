
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

client = MongoClient(MONGO_URI); db = client[DB_NAME]; docs_col = db["docs"]
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query: str, k:int=3):
    docs = list(docs_col.find({}, {"content":1, "embedding":1, "filename":1}))
    if not docs: return []
    q_emb = embedder.encode([query], convert_to_numpy=True)
    X = np.array([d["embedding"] for d in docs])
    sims = cosine_similarity(q_emb, X)[0]
    idxs = sims.argsort()[::-1][:k]
    return [{"filename": docs[i]["filename"], "content": docs[i]["content"], "score": float(sims[i])} for i in idxs]
