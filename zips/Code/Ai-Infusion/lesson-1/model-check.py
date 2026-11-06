from llm_client import invoke_llmquery

query = invoke_llmquery(
        "You are a witty travel assistant.",
        "Suggest a one unique travel destination for a solo traveler who loves adventure and nature in Hyderabad",
        model="gemini-3.1-flash-lite",
        reasoning_effort="minimal",
        provider="gemini"
) 

print(query) 