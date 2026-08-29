from langchain_groq import ChatGroq
import os

def get_llm():
    return ChatGroq(
        api_key="your_groq_key_here",
        model="allam-2-7b",
        temperature=0,
        max_tokens=300
    )

def ask_llm(prompt: str) -> str:
    llm = get_llm()
    system = "You are a payment AI. Return ONLY valid JSON. No explanation. No markdown. No extra text."
    from langchain_core.messages import HumanMessage, SystemMessage
    result = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=prompt)
    ])
    return result.content.strip()