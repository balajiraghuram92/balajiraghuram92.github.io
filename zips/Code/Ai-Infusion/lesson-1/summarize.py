from llm_client import invoke_llmquery
from scrapper import fetch_website_data

system_prompt = """You analyze the contents of a website and
give a short, friendly summary. Ignore navigation menus.
Respond in markdown."""

def summarize(url):
    website = fetch_website_data(url)
    return invoke_llmquery(
        system_prompt,
        f"Summary this website: \n\n{website}",
        model="gemini-3.1-flash-lite",        
        provider="gemini",
    )
 