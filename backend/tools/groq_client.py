from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="allam-2-7b",
        temperature=0,
        max_tokens=300
    ) 

def ask_llm(prompt: str) -> str:
    llm = get_llm()
    from langchain_core.messages import HumanMessage, SystemMessage
    result = llm.invoke([
        SystemMessage(content="You are a payment AI. Return ONLY valid JSON. No explanation. No markdown. No extra text."),
        HumanMessage(content=prompt)
    ])
    return result.content.strip()