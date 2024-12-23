from langchain.tools.retriever import create_retriever_tool
from app.services.Chroma_service import get_chroma_vector_store,local_Rag
from langchain.tools import tool
from app.utils.quantitative import query_eth_indicators
from web3 import Web3
from eth_account import Account
import time
import json
def GetTools():
    tools = [BuyCryptos]
    return tools


@tool
def BuyCryptos(trade_type: str, input_token: str, output_token: str, amount: float) ->str:
    """
    tools for buy and sell Cryptos
    trade_type : ETH_TO_TOKEN  or TOKEN_TO_ETH , for Buying ETH use TOKEN_TO_ETH , for selling ETH use ETH_TO_TOKEN
    input_token : ETH or BNB
    output_token: ETH or BNB
    amount : specifi amount 
    """
    if input_token == "ETH":
        input = "0xeD24FC36d5Ee211Ea25A80239Fb84Cfd80f12Ee"


    print( f"{trade_type} {input_token} {output_token} accept")
    return f"{amount} done sucess"

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




# ERC20代币的ABI
token_abi = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

class BuyCryptos:
    def __init__(self, trade_type=None, input_token=None, output_token=None, amount=None):
        """
        初始化交易参数
        :param trade_type: 交易类型 (ETH_TO_TOKEN, TOKEN_TO_ETH, TOKEN_TO_TOKEN)
        :param input_token: 输入代币地址
        :param output_token: 输出代币地址
        :param amount: 交易数量
        """
        self.trade_type = trade_type
        self.input_token = input_token
        self.output_token = output_token
        self.amount = amount

        # 初始化 Web3
        self.w3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-2-s1.binance.org:8545/'))
        
        # 合约地址
        self.AGENT_ADDRESS = Web3.to_checksum_address("0x0aa156eebbe3a8921492491c3829444024502c9b")  # 合约地址
        self.WBNB = Web3.to_checksum_address("0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd")

        # 加载合约 ABI
        with open("app/abis/agent_abi.json", "r") as f:
            self.agent_abi = json.load(f)

        # 创建合约实例
        self.agent_contract = self.w3.eth.contract(
            address=self.AGENT_ADDRESS,
            abi=self.agent_abi
        )

        # 创建账户
        self.private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        self.account = Account.from_key(self.private_key)

    def check_balances(self):
        """检查用户余额"""
        eth_balance = self.agent_contract.functions.getETHBalance().call({'from': self.account.address})
        print(f"当前ETH余额: {self.w3.from_wei(eth_balance, 'ether')} ETH")

        if self.trade_type != 'ETH_TO_TOKEN':
            token_balance = self.agent_contract.functions.getTokenBalance(self.input_token).call({'from': self.account.address})
            print(f"当前代币余额: {self.w3.from_wei(token_balance, 'ether')} Token")
            return token_balance >= self.w3.to_wei(self.amount, 'ether')

        return eth_balance >= self.w3.to_wei(self.amount, 'ether')

    def execute_trade(self):
        """执行交易"""
        try:
            # 检查余额
            if not self.check_balances():
                return "余额不足"

            # 准备通用参数
            amount_in = self.w3.to_wei(self.amount, 'ether')
            deadline = int(time.time()) + 600  # 10分钟后过期
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            path = [self.input_token, self.output_token]

            # 根据交易类型执行不同的交易
            if self.trade_type == "ETH_TO_TOKEN":
                # 计算最小输出金额（允许 10% 滑点）
                amount_out_min = int(amount_in * 0.9)
                
                # 构建交易
                transaction = self.agent_contract.functions.swapETHForTokens(
                    self.account.address,
                    amount_out_min,
                    path,
                    deadline
                ).build_transaction({
                    'from': self.account.address,
                    'value': amount_in,
                    'gas': 200000,
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': nonce,
                    'chainId': 97
                })

            elif self.trade_type == "TOKEN_TO_ETH":
                # 计算最小输出金额（允许 10% 滑点）
                amount_out_min = int(amount_in * 0.9)
                
                # 构建交易
                transaction = self.agent_contract.functions.swapTokensForETH(
                    self.account.address,
                    amount_in,
                    amount_out_min,
                    path,
                    deadline
                ).build_transaction({
                    'from': self.account.address,
                    'value': 0,
                    'gas': 200000,
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': nonce,
                    'chainId': 97
                })

            elif self.trade_type == "TOKEN_TO_TOKEN":
                # 计算最小输出金额（允许 10% 滑点）
                amount_out_min = int(amount_in * 0.9)
                
                # 构建交易
                transaction = self.agent_contract.functions.swapTokensForTokens(
                    self.account.address,
                    amount_in,
                    amount_out_min,
                    path,
                    deadline
                ).build_transaction({
                    'from': self.account.address,
                    'value': 0,
                    'gas': 200000,
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': nonce,
                    'chainId': 97
                })

            else:
                return f"不支持的交易类型: {self.trade_type}"

            # 签名并发送交易
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"交易已发送，等待确认... Hash: {tx_hash.hex()}")
            
            # 等待交易确认
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # 检查交易状态
            if tx_receipt['status'] == 1:
                return f"Successfully executed {self.trade_type} trade. Transaction hash: {tx_hash.hex()}"
            else:
                return f"Transaction failed. Transaction hash: {tx_hash.hex()}"

        except Exception as e:
            return f"Error executing trade: {e}"

    def deposit_eth(self, amount):
        """存入ETH"""
        try:
            amount_in_wei = self.w3.to_wei(amount, 'ether')
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # 构建交易
            transaction = self.agent_contract.functions.depositETH().build_transaction({
                'from': self.account.address,
                'value': amount_in_wei,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
                'chainId': 97
            })
            
            # 签名并发送交易
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"存款交易已发送，等待确认... Hash: {tx_hash.hex()}")
            
            # 等待交易确认
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt['status'] == 1:
                return f"Successfully deposited {amount} ETH. Transaction hash: {tx_hash.hex()}"
            else:
                return f"Deposit failed. Transaction hash: {tx_hash.hex()}"
                
        except Exception as e:
            return f"Error depositing ETH: {e}"

    def deposit_token(self, token_address, amount):
        """存入代币"""
        try:
            amount_in_wei = self.w3.to_wei(amount, 'ether')
            
            # 创建 ERC20 合约实例
            erc20_abi = [
                {
                    "constant": False,
                    "inputs": [
                        {"name": "_spender", "type": "address"},
                        {"name": "_value", "type": "uint256"}
                    ],
                    "name": "approve",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }
            ]
            token_contract = self.w3.eth.contract(address=token_address, abi=erc20_abi)
            
            # 授权代币
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            approve_tx = token_contract.functions.approve(
                self.AGENT_ADDRESS,
                amount_in_wei
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
                'chainId': 97
            })
            
            # 签名并发送授权交易
            signed_approve_tx = self.w3.eth.account.sign_transaction(approve_tx, self.private_key)
            approve_tx_hash = self.w3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
            print(f"授权交易已发送，等待确认... Hash: {approve_tx_hash.hex()}")
            self.w3.eth.wait_for_transaction_receipt(approve_tx_hash)
            print("代币授权成功")
            
            # 存入代币
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            transaction = self.agent_contract.functions.depositERC20(
                token_address,
                amount_in_wei
            ).build_transaction({
                'from': self.account.address,
                'value': 0,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
                'chainId': 97
            })
            
            # 签名并发送交易
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"存款交易已发送，等待确认... Hash: {tx_hash.hex()}")
            
            # 等待交易确认
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt['status'] == 1:
                return f"Successfully deposited {amount} tokens. Transaction hash: {tx_hash.hex()}"
            else:
                return f"Deposit failed. Transaction hash: {tx_hash.hex()}"
                
        except Exception as e:
            return f"Error depositing tokens: {e}"
