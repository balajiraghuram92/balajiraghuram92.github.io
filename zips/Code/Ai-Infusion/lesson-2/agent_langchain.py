from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
prices =  {"shoes": 799, "hat": 399, "bag": 1420, "shorts": 1299, "pants": 1699, "iphone": 999}

"""" GOOGLE API MODEL
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI 

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key= os.getenv("GEMINI_API_KEY") 
)
""" 

"""  GLM 4.7 Flah AWS Bedrock
model = ChatOpenAI(
        model="zai.glm-4.7-flash",
        api_key=os.getenv("ANTHROPIC_API_KEY"),        # your Bedrock key
        base_url=os.getenv("BEDROCK_OPENAI_URL"),      # https://bedrock-mantle.ap-south-1.api.aws/v1
        temperature=0.3,
        )
"""

""" # Mini Max 2.4 AWS Bedrock
model = ChatOpenAI(
        model="minimax.minimax-m2.5",
        api_key=os.getenv("ANTHROPIC_API_KEY"),        # your Bedrock key
        base_url=os.getenv("BEDROCK_OPENAI_URL"),      # https://bedrock-mantle.ap-south-1.api.aws/v1
        temperature=0.3,
        )
""" 
# DeepInfra Deepseek V4  

model = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V4-Flash-0731",
    api_key=os.getenv("DEEPINFRA_API_KEY"),
    base_url=os.getenv("DEEPINFRA_API_URL"),
    reasoning_effort="none",      # thinking off: faster, and avoids tool-loop issues
    temperature=0.3,
) 
#""""

@tool
def get_price(item : str) -> str:
    """Get the price of a shop ite, the user has asked about."""
    print(f"tool called: get_price({item})")
    return f"${prices.get(item.lower(), 'unknown')}"

model_with_tools = model.bind_tools([get_price])

def to_text(content):
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content if isinstance(part, dict))

def convert_history(history):
    messages = []
    for turn in history:
        text = to_text(turn["content"])
        if turn["role"] == "user":
            messages.append(HumanMessage(text))
        elif turn["role"] == "assistant":
            messages.append(AIMessage(text))
        
    ai_instruct = "only provide cost of items you can find through tool call, if you do not get the price of any item, return price of an item is not found or out of stock message to user"
    messages.append(ai_instruct)

    return messages


def agent(user_message, history = None):
    if history is None:
        history = []

    messages = convert_history(history)
    messages.append(HumanMessage(user_message))

    ai_msg = model_with_tools.invoke(messages)

    if ai_msg.tool_calls:
        messages.append(ai_msg)
        for call in ai_msg.tool_calls:
            result = get_price.invoke(call["args"])
            messages.append(ToolMessage(content= result, tool_call_id=call["id"]))
        ai_msg = model_with_tools.invoke(messages)

    return ai_msg.content

if __name__ == "__main__":
    print(agent("How much are the shoes"))
    print(agent("Hi! What can you help with?"))

