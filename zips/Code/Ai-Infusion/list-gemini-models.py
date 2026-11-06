import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available Gemini models:\n")
for model in genai.list_models():
    print(f"Model: {model.name}")
    print(f"  Display Name: {model.display_name}")
    print(f"  Input Token Limit: {model.input_token_limit}")
    print(f"  Supported Methods: {model.supported_generation_methods}")
    print()
