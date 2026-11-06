import gradio as gr
from agent_langchain import agent, to_text

def chat(message, history):
    if message.strip().lower() in {"bye" , "quit" , "exit"}:
        return " a google bye string"
    
    reply = agent(message, history)
    return to_text(reply)


gr.ChatInterface(
    fn=chat, 
    title="🛍️ Smart Shop Assistant",
    description= "Ask me the price of shoes, hat, bag or pants - I can get the prices of those items"
).launch()






 