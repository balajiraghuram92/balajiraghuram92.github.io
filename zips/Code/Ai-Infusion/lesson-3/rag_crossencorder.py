from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
import os
from sentence_transformers import CrossEncoder

embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory = "./chroma_db", embedding_function= embedder)
model = ChatOpenAI(
        model="deepseek-ai/Deepseek-V4-Flash-0731",
        api_key=os.getenv("DEEPINFRA_API_KEY"),
        base_url=os.getenv("DEEPINFRA_API_URL"),
        reasoning_effort="none",
        temperature=0.3
)

prompt = ChatPromptTemplate.from_template(
    """
        Answer the question using ONLY the context below. If the content doesn't contain the answer. 
        then say "I don't Know." Be concise and quote facts directly.

        Context:{context}

        Question:{question} 
    """
)

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
chain = prompt | model 

def retrive_rag_with_rerank(question, top_k=3):
    candidates = db.similarity_search(question, k =25)
    pairs = [(question, c.page_content) for c in candidates]
    scores = reranker.predict(pairs)
    return [c for _, c in sorted(zip(scores, candidates), key=lambda pair:pair[0],reverse=True)[:top_k]]

def rag_answer(question):
    docs = retrive_rag_with_rerank(question)
    context = "\n\n".join(d.page_content for d in docs)
    return chain.invoke({"context": context, "question": question}).content
   
if __name__ == "__main__":
    print(rag_answer("how long do i have to return something?"))
    print(rag_answer("Do you sell laptops?"))

