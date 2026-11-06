import json
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI( api_key = os.getenv("GEMINI_API_KEY"), base_url =  os.getenv("GEMINI_API_URL"))

prices =  {"shoes": 799, "hat": 399, "bag": 1420, "shorts": 1299, "pants": 1699}

def get_price(item):
    print(f"tool called: get_price({item})")
    return f"${prices.get(item.lower(), 'unknown')}"

tool = [{
            "type" : "function",
            "function": {
                "name" : "get_price",
                "description" : " Get the price of a shop item  the user has asked about",
                "parameters":{
                    "type" :"object",
                    "properties": {"item" : { "type" : "string", "description" : " the item name"}},
                    "required" : ["item"],
                    },
                },
        }]


def agent(user_message):
    messages = [{
                "role" : "user", "content": user_message  }]

    response = client.chat.completions.create(
        model = "gemini-3.1-flash-lite",
        messages = messages,
        tools = tool
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        messages.append(msg)
        for call in msg.tool_calls:
            arg = json.loads(call.function.arguments)
            result = get_price(arg["item"]) 
            messages.append({"role" : "tool", "tool_call_id": call.id, "content" : result})
        response = client.chat.completions.create(
                    model = "gemini-3.1-flash-lite",
                    messages = messages)
        msg = response.choices[0].message

    return msg.content


if __name__ == "__main__":
    print(agent("How much are the price for the shoes?\n \n \n \n"))
    print(agent("Hi ! What can you help with? \n \n"))
            