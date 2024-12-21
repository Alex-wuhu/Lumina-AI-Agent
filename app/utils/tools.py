from langchain.tools.retriever import create_retriever_tool
from app.services.Chroma_service import get_chroma_vector_store,local_Rag
from langchain.tools import tool
from web3 import Web3
from eth_account import Account
import time


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


def BuyCryptos(trade_type: str, input_token: str, output_token: str, amount: float) -> str:
    try:
        # 连接到 BSC 测试网
        w3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-1-s1.binance.org:8545'))

        # 合约地址
        OWNER_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        BACKEND_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        PANCAKE_ROUTER = "0x9Ac64Cc6e4415144C455BD8E4837Fea55603e5c3"
        WBNB_ADDRESS = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"

        # 设置账户私钥
        private_key = 'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
        account = Account.from_key(private_key)

        # PancakeSwap Router ABI
        router_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactETHForTokens",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactTokensForETH",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactTokensForTokens",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

        # 初始化合约
        contract = w3.eth.contract(address=PANCAKE_ROUTER, abi=router_abi)

        # 准备通用参数
        amount_in = w3.to_wei(amount, 'ether')
        amount_out_min = w3.to_wei(amount * 0.99, 'ether')  # 1% 滑点
        deadline = int(time.time()) + 1800  # 30分钟后过期

        # 根据交易类型准备交易
        if trade_type == 'ETH_TO_TOKEN':
            path = [WBNB_ADDRESS, output_token]
            transaction = contract.functions.swapExactETHForTokens(
                amount_out_min,
                path,
                OWNER_ADDRESS,  # 接收代币的地址
                deadline
            ).build_transaction({
                'from': BACKEND_ADDRESS,
                'value': amount_in,  # 发送的 ETH 数量
                'gas': 2000000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(BACKEND_ADDRESS),
            })

        elif trade_type == 'TOKEN_TO_ETH':
            path = [input_token, WBNB_ADDRESS]
            transaction = contract.functions.swapExactTokensForETH(
                amount_in,
                amount_out_min,
                path,
                OWNER_ADDRESS,  # 接收 ETH 的地址
                deadline
            ).build_transaction({
                'from': BACKEND_ADDRESS,
                'gas': 2000000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(BACKEND_ADDRESS),
            })

        elif trade_type == 'TOKEN_TO_TOKEN':
            path = [input_token, output_token]
            transaction = contract.functions.swapExactTokensForTokens(
                amount_in,
                amount_out_min,
                path,
                OWNER_ADDRESS,  # 接收代币的地址
                deadline
            ).build_transaction({
                'from': BACKEND_ADDRESS,
                'gas': 2000000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(BACKEND_ADDRESS),
            })
        else:
            return f"Invalid trade type: {trade_type}"

        # 签名并发送交易
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # 等待交易收据
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt['status'] == 1:
            return f"Successfully executed {trade_type} trade. Transaction hash: {tx_hash.hex()}"
        else:
            return f"Transaction failed for {trade_type}"

    except Exception as e:
        return f"Error executing trade: {str(e)}"
