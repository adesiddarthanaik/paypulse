from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings
import os

CHROMA_PATH = "./chroma_db"

def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

def store_case(payment_id: str, failure_code: str, intervention: str, outcome: str):
    vs = get_vectorstore()
    text = f"Payment {payment_id}: {failure_code} → {intervention} → {outcome}"
    vs.add_texts(
        texts=[text],
        metadatas=[{
            "payment_id": payment_id,
            "failure_code": failure_code,
            "intervention": intervention,
            "outcome": outcome
        }]
    )

def retrieve_similar_cases(failure_code: str, amount: float, k: int = 3) -> list:
    try:
        vs = get_vectorstore()
        query = f"Payment failure: {failure_code}, amount: {amount}"
        results = vs.similarity_search(query, k=k)
        return [r.page_content for r in results]
    except:
        return []