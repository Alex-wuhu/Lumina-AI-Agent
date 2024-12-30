from app.services.LLM_service import get_response
from app.utils.quantitative import query_eth_indicators

prompt2 = f"""
You are an AI assistant designed to manage cryptocurrency trading 
1. currently you have 10 BNB and 1ETH
2. current ETH indicators are {query_eth_indicators()}
3. based on current indicators make specific Buy/sell Commands with current USDT for more profit, 
    you are a High risk trader
Example1
    Current ETH price is 3392, Based on Quantitative analysis
    Use 8 BNB for buying ETH , cause ETH has a potential uptrend
Example2
    Current ETH price is 3392, Based on Quantitative analysis
    Use 1 ETH for buying BNB , cause ETH has a potential downtrend
Example3
    Based on Quantitative analysis, the best way for more profit is do nothing and wait.
"""
get_response(prompt2)


