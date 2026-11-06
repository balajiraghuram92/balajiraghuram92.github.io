import os, sys, time 
import chromadb
from chromadb.utils import embedding_functions
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from dotenv import load_dotenv 
load_dotenv()

app = FastAPI(title="ScalerGPT") 
API_KEY = os.getenv("DEEPINFRA_API_KEY")
API_URL = os.getenv("DEEPINFRA_API_URL")

llm = OpenAI( 
    api_key= API_KEY,
    base_url= API_URL
    )

if not API_KEY or API_KEY.startswith("paste"):
    sys.exit("[ingest] DEEP INFRA API key is missing add it in the .env file")

openai_embedding = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY, api_base=API_URL, model_name="BAAI/bge-base-en-v1.5")

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8001")

def connect_to_chroma(retries=30,delay=2):
    for attempt in range(1, retries + 1):
        try:
            client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            client.heartbeat()
            print(f"[ScalerGPT] connected to chroma at {CHROMA_HOST}:{CHROMA_PORT}", flush=True)
            return client
        except Exception as e:
            print(f"[ScalerGPT] Waiting for chroma({attempt} / {retries}) : {type(e).__name__}", flush=True)
            time.sleep(delay)
    sys.exit(f"[ScalerGPT] could not reach chroma db at {CHROMA_HOST}:{CHROMA_PORT}")

chroma = connect_to_chroma()
collection = chroma.get_or_create_collection(name="notes", embedding_function=openai_embedding)

class Question(BaseModel):
    query: str

@app.get("/health")
def health():
    return {
        "status" : "ScalerGPT is live",
        "docs_indexed": collection.count(),
        "chroma_host": CHROMA_HOST,
        "chroma_port" : CHROMA_PORT}

@app.post("/ask")
def ask(q:Question):
    if collection.count() == 0:
        raise HTTPException(status_code= 400,
                            detail= "No documents indexed. Run: docker compose exec app pthon ingest.py")
    hits = collection.query(query_texts = [q.query], n_results=3)
    documents = hits.get("documents") or [[]]
    context = "\n\n-----\n\n".join(documents[0])
    system_prompt = ("You are ScalerGPT, a helpful teaching assistant." 
                      "Answer using ONLY the context below. If it does not contain the asnwer. "
                    f"say you don't know. \n\nCONTEXT:\n{context}")
    resp = llm.chat.completions.create(model="deepseek-ai/Deepseek-V4-Flash-0731",
                                       messages=[
                                            {"role" : "system", "content": system_prompt},
                                            {"role" : "user", "content": q.query}])
    return {"question" : q.query, "answer": resp.choices[0].message.content,
            "sources_used" :len(documents[0])}


    