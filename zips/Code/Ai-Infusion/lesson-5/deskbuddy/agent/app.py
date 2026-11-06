import os, json, sys
import redis, httpx
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

app = FastAPI(title="DeskBuddy")

llm = OpenAI(
    api_key=os.getenv("DEEPINFRA_API_KEY"),
    base_url=os.getenv("DEEPINFRA_API_URL"))

class Chat(BaseModel):
    session_id: str
    message: str


REDDIS_HOST = os.getenv("REDIS_HOST", "redis") 

r = redis.Redis(
    REDDIS_HOST, 
    port=6379,
    decode_responses=True)

TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:7000")
TOOL_DEFS = [
    {
        "type" :"function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a math expression, e.g '23*47' or (100-8)/4",
            "parameters":{
                "type" : "object",
                "properties" : {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },

    },
    {
        "type" : "function",
        "function": {
            "name" : "get_datetime",
            "description": "Get the current data and time",
            "parameters": {"type" : "object", "properties": {}},
        },
    },
]

def call_tool(name: str, args: dict) -> dict:
    """Actually excute a tool by calling the tools microservice over HTPP."""

    try:
        if name == "calculator":
            return httpx.post(f"{TOOLS_URL}/calculator", json=args, timeout=10).json()
        elif name =="get_datetime":
            return httpx.get(f"{TOOLS_URL}/datetime", timeout=10).json()
        return {"error": f"unkown tool: {name}"}
    except Exception as e:
        return {"error" : f"tool call failed: {e}"}


@app.post("/chat")
def chat(req: Chat):
    key = f"history:{req.session_id}"
    history = [json.loads(m) for m in r.lrange(key, 0, -1)]
    history.append({"role": "user", "content": req.message})


    for _ in range(5):
        resp = llm.chat.completions.create(
            model = "deepseek-ai/Deepseek-V4-Flash-0731",
            messages=history,
            tools=TOOL_DEFS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            break
        history.append(msg.model_dump(exclude_none=True))
        for tc in msg.tool_calls:
            result = call_tool(tc.function.name, json.loads(tc.function.arguments))
            history.append(
                {"role" : "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
                }
            )

    history.append(
        {
            "role" : "assistant",
            "content": msg.content
        }
    ) 
    r.delete(key)
    for m in history:
        r.rpush(key, json.dumps(m))

    return { "answer" :msg.content }   
            