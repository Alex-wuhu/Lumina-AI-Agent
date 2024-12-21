from langchain.tools.retriever import create_retriever_tool
from app.services.Chroma_service import get_chroma_vector_store,local_Rag
from langchain.tools import tool



def GetTools():

    vector_store = get_chroma_vector_store()
    retriever = vector_store.as_retriever()
    
    retriever_tool = create_retriever_tool(
        retriever,
        "Bitcoin Quantitative analysis retriever",
        "Search for information about Bitcoin Quantitative analysis. For any questions about Quantitative analysis Bitcoin, you can use this tool",
    )
    tools = [retriever_tool,BuyCryptos]
    return tools

def BuyCryptos(Crypto_Name: str,amount: float) -> str:
    """Try to Buy Crypto with specific amount"""
    #print(f"Buy function triggered {Crypto_Name}, {amount}")
    return f"Buy {amount} {Crypto_Name}success"
