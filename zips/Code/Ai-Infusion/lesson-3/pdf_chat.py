from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder
from langchain_community.retrievers import BM25Retriever
load_dotenv()
import os

model = ChatOpenAI(
    model="deepseek-ai/Deepseek-V4-Flash-0731",
    api_key=os.getenv("DEEPINFRA_API_KEY"),
    base_url=os.getenv("DEEPINFRA_API_URL"),
    reasoning_effort="medium",
    temperature=0.3
)

prompt = ChatPromptTemplate.from_template(
    """
    You are an Helpful PDF assisant. Answer the question using ONLY the content below.
    If the context doesn't have the requested information to anwser the question, say "I don't have enough data to answer to your question"
    After your Answer, list the page numbers you used as : Sources: page X, page Y.

    Content: {Content}

    Question: {question}
    """
)

def build_index(pdf_path):
    pages = PyPDFLoader(pdf_path).load()
    splitter = RecursiveCharacterTextSplitter(chunk_size= 800, chunk_overlap=100)
    chunks = splitter.split_documents(pages)
    embeddder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(chunks,embeddder)
    bm25 = BM25Retriever.from_documents(chunks, k =25)
    return db,bm25


reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
chain = prompt | model
 
def rrf_merge(result_lists, k = 60):
    scores, docs = {}, {}
    for results in result_lists:
        for rank, doc in enumerate(results, start=1):
            key = (doc.metadata.get("page"), doc.page_content)
            scores[key] = scores.get(key, 0) + 1 /(k + rank)
            docs[key] = doc
    ranked = sorted(scores, key=scores.get, reverse=True)
    return [doc[key] for key in ranked]

def hybrid_search(db, bm25, question, k= 25):
    vector_hits = db.similarity_serach(question, k = k)
    keyword_hits = bm25.invoke(question)
    return rrf_merge([vector_hits, keyword_hits])

def ask(db, question, top_k = 3):
    candidates = db.similarity_search(question, k=25)
    pairs=[(question,c.page_content) for c in candidates]
    scores = reranker.predict(pairs) 
    docs = [c for _,c in sorted(zip(scores, candidates), key=lambda pair:pair[0], reverse="True")[:top_k]]
    content = "\n\n".join(d.page_content for d in docs)
    return chain.invoke({"Content":content, "question":question}).content


import gradio as gr

state = {"db": None}

def upload(pdf):
    state["db"], state["bm25"] = build_index(pdf.name) 
    return " PDF indexed! Ask me anything about it."

def chat(message, history):
    if state["db"] is None:
        return "Please upload the pdf"
    return ask(state["db"], message)

with gr.Blocks(title="Chat with your PDF") as demo:
    gr.Markdown(" Chat with your PDF Powered by RAG)")
    pdf = gr.File(label = "Upload a PDF", file_types=[".pdf"])
    status = gr.Markdown()
    pdf.upload(upload, inputs=pdf, outputs=status)
    gr.ChatInterface(fn=chat)


demo.launch();