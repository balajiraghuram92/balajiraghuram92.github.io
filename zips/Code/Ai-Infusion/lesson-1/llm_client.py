import os
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


PROVIDERS = {
    "openai":{
        "api_key": None,
        "base_url": None
    }, 
    
    "groq": {
        "api_key"  : os.getenv("GROQ_API_KEY"),
        "base_url" : os.getenv("GROQ_API_URL")
    },

    "gemini":{
        "api_key" : os.getenv("GEMINI_API_KEY"),
        "base_url" : os.getenv("GEMINI_API_URL")
    },

    "muse_ai": {
        "api_key" : os.getenv("MUSE_AI_API_KEY"),
        "base_url" : os.getenv("MUSE_API_URL")
    }, 
}


@lru_cache(maxsize=None)
def get_client(provider="openai"):
    cfg = PROVIDERS[provider]
    return OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])

def invoke_llmquery(system_msg,user_msg,model="gpt-4o-mini", reasoning_effort=None,provider="openai"):
    kwagrs= {}
    if reasoning_effort:
        kwagrs["reasoning_effort"] = reasoning_effort 

    response_object = get_client(provider).chat.completions.create(
                            model=model,
                            messages=[{"role": "system", "content" : system_msg},
                                    {"role": "user", "content": user_msg}],
                            **kwagrs,        
                        ) 

    return response_object.choices[0].message.content