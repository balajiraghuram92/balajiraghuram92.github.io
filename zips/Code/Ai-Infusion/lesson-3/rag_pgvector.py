
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_postgres import PGEngine, PGVectorStore

load_dotenv() 
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

model = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V4-Flash-0731",
    api_key=os.getenv("DEEPINFRA_API_KEY"),
    base_url=os.getenv("DEEPINFRA_API_URL"),
    reasoning_effort="none",      
    temperature=0.3,
)  

url = (
    f"postgresql+psycopg://{os.getenv('PG_USER')}:{quote_plus(os.getenv('PG_PASSWORD'))}"
    f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
)

engine = PGEngine.from_connection_string(url=url)
table = "user_doc"
store = PGVectorStore.create_sync(engine=engine, table_name=table, embedding_service=embedder) 

prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the content below. 
If the content doesn't contain the answer, say "I don't know." 
Be concise and quote facts directory.

Content: {content}

Question: {question}
""")    

chain = prompt | model | StrOutputParser()

def rag_answer(question: str) -> str:
    docs= store.similarity_search(question, k=3)
    print("Retrieved", [d.page_content for d in docs])
    content = "\n\n".join(d.page_content for d in docs)
    return chain.invoke({"content": content, "question" : question})

if __name__ == "__main__":
    print(rag_answer("how long do i have to return something?"))
    print(rag_answer("Do you sell laptops?"))



