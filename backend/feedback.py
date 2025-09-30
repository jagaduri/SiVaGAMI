
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from datetime import datetime

client = MongoClient(MONGO_URI); db = client[DB_NAME]; feedback_col = db["feedback"]

def save_feedback(record: dict):
    r = record.copy(); r["created_at"] = datetime.utcnow(); feedback_col.insert_one(r)

def get_metrics():
    docs = list(feedback_col.find({}).sort("created_at", 1))
    items=[]; correct=0
    for i, d in enumerate(docs):
        if d.get("feedback") in ("correct", True): correct += 1
        items.append({"step": i+1, "accuracy": round(100.0*correct/(i+1),2)})
    return items
