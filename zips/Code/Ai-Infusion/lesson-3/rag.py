from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
import os

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

chain = prompt | model 
def rag_answer(question):
    chunks = db.similarity_search(question, k = 3)
    context = "\n\n".join(c.page_content for c in chunks)
    return chain.invoke({"context": context, "question": question}).content

if __name__ == "__main__":
    print(rag_answer("how long do i have to return something?"))
    print(rag_answer("Do you sell laptops?"))

