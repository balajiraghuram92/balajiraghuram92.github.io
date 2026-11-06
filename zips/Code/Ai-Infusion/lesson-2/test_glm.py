# test_glm.py
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
     api_key=os.getenv("ANTHROPIC_API_KEY"),
     base_url=os.getenv("BEDROCK_OPENAI_URL")   # https://bedrock-mantle.ap-south-1.api.aws/v1
)
MODEL = "zai.glm-4.7-flash"

# Test 1: plain answer
start = time.perf_counter()
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)
print(f"[plain] {time.perf_counter() - start:.2f}s")
print(response.choices[0].message.content, "\n")

# Test 2: does it ask for a tool?
tools = [{
    "type": "function",
    "function": {
        "name": "get_price",
        "description": "Get the price of a shop item the user has asked about.",
        "parameters": {
            "type": "object",
            "properties": {"item": {"type": "string", "description": "the item name"}},
            "required": ["item"],
        },
    },
}]

start = time.perf_counter()
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "How much are the shoes?"}],
    tools=tools,
)
msg = response.choices[0].message
print(f"[tool] {time.perf_counter() - start:.2f}s")
print("tool calls:", msg.tool_calls)