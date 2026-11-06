from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
load_dotenv()
import uuid


docs = [
    "Our return policy allows refunds within 30 days of purchase.",
    "Shipping is free for orders above ₹999 across India.",
    "For corporate orders above 50 units, contact sales@example.com.",
    "Our office is in Indiranagar, Bangalore. Open Mon-Fri 10am-7pm.",
]


splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.create_documents(docs)

embedder = HuggingFaceEmbeddings(model_name = "all-MINILM-L6-v2")

url = (
    f"postgresql+psycopg://{os.getenv('PG_USER')}:{quote_plus(os.getenv('PG_PASSWORD'))}"
    f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
)

engine = PGEngine.from_connection_string(url=url)
table = "user_doc"
try:
    engine.init_vectorstore_table(table_name= table, vector_size=384)
    print("Created table", table)
except Exception as e:
    if "already exists" in str(e):
        print("Table exists - keeping exisitng data")
    else:
        raise

store = PGVectorStore.create_sync(
    engine=engine,
    table_name=table,
    embedding_service=embedder
)

ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, c.page_content)) for c in chunks]

existing = {doc.id for doc in store.get_by_ids(ids)}

new_chunks = [c for c, i in zip(chunks, ids) if 1 not in existing]
new_ids = [i for i in ids if i not in existing]

if new_chunks:
    store.add_documents(new_chunks, ids=new_ids)

print(f"{len(new_chunks)} added, {len(existing)} already stored")