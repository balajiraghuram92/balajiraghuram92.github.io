import glob, os, sys, time
import chromadb
from chromadb.utils import embedding_functions

API_KEY = os.getenv("DEEPINFRA_API_KEY")
API_URL = os.getenv("DEEPINFRA_API_URL")

if not API_KEY or API_KEY.startswith("sk-paste"):
    sys.exit("[ingest] DEEP INFRA API key is missing. Put a real key in .env and recreate.")

openai_embedding = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY, api_base=API_URL, model_name="BAAI/bge-base-en-v1.5")


host = os.getenv("CHROMA_HOST", "localhost")
port = int(os.getenv("CHROMA_PORT", "8000"))

chroma = None
for attempt in range(10):
    try:
        chroma = chromadb.HttpClient(host=host, port=port)
        chroma.heartbeat()
        break
    except Exception:
        print(f"[ingest] waiting for chroma ({attempt + 1}/10)...", flush=True)
        time.sleep(2)
if chroma is None:
    sys.exit(f"[ingest] Could not reach chroma at {host}:{port}")

collection = chroma.get_or_create_collection(name="notes", embedding_function=openai_embedding)

files = sorted(glob.glob("docs/*.txt") + glob.glob("docs/*.md"))
if not files:
    sys.exit("No files found in docs/ — add some .txt or .md notes first.")

ids, documents, metadatas = [], [], []
for path in files:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    # Simple chunking: split on blank lines, keep chunks of reasonable size
    chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 40]

    for i, chunk in enumerate(chunks):
        ids.append(f"{os.path.basename(path)}::{i}")
        documents.append(chunk)
        metadatas.append({"source": os.path.basename(path)})

if not documents:
    sys.exit("Files found but no usable chunks. Make paragraphs a bit longer.")

# upsert = add or overwrite, so re-running this script is safe
collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

print(f"Ingested {len(documents)} chunks from {len(files)} file(s) ✅")
print(f"Collection now holds {collection.count()} chunks total.")
