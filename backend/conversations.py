from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from datetime import datetime
from bson.objectid import ObjectId

client = MongoClient(MONGO_URI); db = client[DB_NAME]
convs = db["conversations"]; msgs = db["messages"]

def start_conversation(title: str = "New chat") -> str:
    doc = {"title": title, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    rid = convs.insert_one(doc).inserted_id
    return str(rid)

def rename_conversation(conv_id: str, title: str):
    convs.update_one({"_id": ObjectId(conv_id)}, {"$set": {"title": title, "updated_at": datetime.utcnow()}})

def delete_conversation(conv_id: str):
    """Delete a conversation and all its messages."""
    convs.delete_one({"_id": ObjectId(conv_id)})
    msgs.delete_many({"conv_id": conv_id})

def list_conversations(limit: int = 50):
    it = convs.find({}).sort("updated_at", -1).limit(limit)
    out=[]
    for c in it:
        last = msgs.find({"conv_id": str(c["_id"])}).sort("ts",-1).limit(1)
        last_text = ""
        for m in last: last_text = m.get("text","")
        out.append({"id": str(c["_id"]), "title": c.get("title",""), "updated_at": c.get("updated_at"), "last": last_text})
    return out

def add_message(conv_id: str, sender: str, text: str):
    msgs.insert_one({"conv_id": conv_id, "sender": sender, "text": text, "ts": datetime.utcnow()})
    convs.update_one({"_id": ObjectId(conv_id)}, {"$set": {"updated_at": datetime.utcnow()}})

def get_messages(conv_id: str, limit: int = 200):
    it = msgs.find({"conv_id": conv_id}).sort("ts", 1).limit(limit)
    return [{"sender": m.get("sender"), "text": m.get("text"), "ts": m.get("ts")} for m in it]
