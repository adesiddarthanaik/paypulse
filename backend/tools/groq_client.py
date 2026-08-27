from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="allam-2-7b",
        temperature=0.1,
        max_tokens=200
    )