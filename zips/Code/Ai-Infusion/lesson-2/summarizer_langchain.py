import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from scrapper import fetch_website_contents


load_dotenv()

prompt = ChatPromptTemplate.from_template(
    "Give a short, a friendly summary of the website: \n\n {website}")

model = ChatOpenAI(
        model="gemini-3.1-flash-lite",
        api_key = os.getenv("GEMINI_API_KEY"),
        base_url=  os.getenv("GEMINI_API_URL"),
        temperature = 0.3
        )

parser = StrOutputParser()

chain = prompt | model | parser

def summarizer(url):
    return chain.invoke({"website": fetch_website_contents(url)})

if __name__ == "__main__":
    print(summarizer("Anthropic.com"))
