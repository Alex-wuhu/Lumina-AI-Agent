from app.services.Chroma_service import get_chroma_vector_store,local_Rag
from langchain.tools import tool

from app.utils.buyCryptos import BuyCryptos


def GetTools():
    tools = [BuyCryptos]
    return tools

@tool
def retrieve(query: str) -> str:
    """Retrieve information related to Quantitative analysis and crypto trading from our knowledge base."""
    # Create a retriever tool with the vector store
    vector_store = get_chroma_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    # Get relevant documents
    docs = retriever.get_relevant_documents(query)

    # Format the response
    response = []
    for doc in docs:
        response.append(f"Source: {doc.metadata}")
        response.append(f"Content: {doc.page_content}")
        response.append("---")

    return "\n".join(response)


@tool
def GetEthIndicators() -> dict:
    """Query current ETH price indicators including last price, VWAP and RSI. Only call this once."""
    indicators = query_eth_indicators()
    return indicators

@tool
def buyCryptos(trade_type: str, input_token: str, output_token: str, amount: float) -> str:

    if input_token == "ETH":
        input = "0xeD24FC36d5Ee211Ea25A80239Fb84Cfd80f12Ee"
    if input_token == "BNB":
        input = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"
    if output_token == "ETH":
        output = "0xeD24FC36d5Ee211Ea25A80239Fb84Cfd80f12Ee"
    if output_token == "BNB":
        output = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"

    trade = BuyCryptos(
        trade_type = trade_type,
        input_token = input,
        output_token = output,
        amount = amount
    )

    # 执行交易
    result = trade.execute_trade()
    print(f"交易结果: {result}")
    print(f"{trade_type} {input_token} {output_token} accept")
    return f"{amount} done sucess"