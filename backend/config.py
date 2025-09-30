
import os

# Mongo
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "sivagami_full")

# Providers
DEFAULT_PROVIDER = os.getenv("PROVIDER", "ollama")  # 'ollama' or 'openai'

# Ollama
OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434")
OLLAMA_MODEL_DEFAULT = os.getenv("OLLAMA_MODEL", "mistral")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_DEFAULT = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Artifacts
ARTIFACT_DIR = os.getenv("ARTIFACT_DIR", "artifacts"); os.makedirs(ARTIFACT_DIR, exist_ok=True)

# Scheduler
WATCH_DIR = os.getenv("WATCH_DIR", "watched"); os.makedirs(WATCH_DIR, exist_ok=True)
