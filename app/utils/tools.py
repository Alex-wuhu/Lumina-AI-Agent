from web3 import Web3
from eth_account import Account
import time
import json

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

def check_transaction_state(w3, account_address, trade_type, input_token, amount):
    """检查交易前的状态"""
    try:
        # 检查ETH余额
        eth_balance = w3.eth.get_balance(account_address)
        print(f"当前ETH余额: {w3.from_wei(eth_balance, 'ether')} ETH")
        
        # 如果是代币交易，检查代币余额
        if trade_type != 'ETH_TO_TOKEN':
            token_contract = w3.eth.contract(address=input_token, abi=token_abi)
            token_balance = token_contract.functions.balanceOf(account_address).call()
            print(f"当前代币余额: {w3.from_wei(token_balance, 'ether')} Token")
            if token_balance < w3.to_wei(amount, 'ether'):
                return False, "代币余额不足"
        
        # 确保有足够的ETH支付gas
        if eth_balance < w3.to_wei(0.01, 'ether'):  # 预留0.01 ETH作为gas
            return False, "ETH余额不足以支付gas费"
            
        return True, "检查通过"
    except Exception as e:
        return False, f"检查失败: {str(e)}"

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

    def execute_trade(self, trade_type=None, input_token=None, output_token=None, amount=None):
        """
        执行代币交易
        :param trade_type: 交易类型 (ETH_TO_TOKEN, TOKEN_TO_ETH, TOKEN_TO_TOKEN)
        :param input_token: 输入代币地址
        :param output_token: 输出代币地址
        :param amount: 交易数量
        :return: 交易结果
        """
        # 如果没有传入参数，使用实例化时的参数
        trade_type = trade_type or self.trade_type
        input_token = input_token or self.input_token
        output_token = output_token or self.output_token
        amount = amount or self.amount

        try:
            # 连接到 BSC 测试网
            w3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-2-s1.binance.org:8545/'))
            
            # 合约地址
            OWNER_ADDRESS = Web3.to_checksum_address("0x0aa156eebbe3a8921492491c3829444024502c9b")
            PANCAKE_ROUTER_ADDRESS = Web3.to_checksum_address("0xD99D1c33F9fC3444f8101754aBC46c52416550D1")

            # 加载合约 ABI
            router_abi = [
                {
                    "inputs": [
                        {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                        {"internalType": "address[]", "name": "path", "type": "address[]"}
                    ],
                    "name": "getAmountsOut",
                    "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                    "stateMutability": "view",
                    "type": "function"
                },
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

            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
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
                    "type": "function"
                }
            ]

            # 创建合约实例
            router_contract = w3.eth.contract(address=PANCAKE_ROUTER_ADDRESS, abi=router_abi)

            # 创建账户
            private_key = "0x227dbb8586117d55284e26620bc76534dfbd2394be34cf4a09cb775d593b6f2b"
            account = Account.from_key(private_key)

            print(f"Account address: {account.address}")
            
            # 检查交易状态
            state_ok, message = check_transaction_state(w3, account.address, trade_type, input_token, amount)
            if not state_ok:
                return f"交易前检查失败: {message}"

            # 准备通用参数
            amount_in = w3.to_wei(amount, 'ether')
            deadline = int(time.time()) + 600  # 10分钟后过期
            nonce = w3.eth.get_transaction_count(account.address)

            # 根据交易类型执行不同的交易
            if trade_type == "ETH_TO_TOKEN":
                # 计算预期输出
                path = [input_token, output_token]
                amounts_out = router_contract.functions.getAmountsOut(amount_in, path).call()
                amount_out_min = int(amounts_out[1] * 0.9)  # 允许 10% 的滑点
                print(f"预期输出金额: {w3.from_wei(amounts_out[1], 'ether')} Token")
                print(f"最小输出金额: {w3.from_wei(amount_out_min, 'ether')} Token")

                # 构建交易
                transaction = router_contract.functions.swapExactETHForTokens(
                    amount_out_min,
                    path,
                    account.address,
                    deadline
                ).build_transaction({
                    'from': account.address,
                    'value': amount_in,
                    'gas': 300000,  # gas 限制
                    'gasPrice': w3.eth.gas_price,  # 使用当前 gas 价格
                    'nonce': nonce,
                    'chainId': 97  # BSC 测试网的 chainId
                })

            elif trade_type == "TOKEN_TO_ETH":
                # 检查代币余额和授权
                token_contract = w3.eth.contract(address=input_token, abi=erc20_abi)
                token_balance = token_contract.functions.balanceOf(account.address).call()
                print(f"当前ETH余额: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} ETH")
                print(f"当前代币余额: {w3.from_wei(token_balance, 'ether')} Token")

                # 检查并授权代币
                print("正在授权代币...")
                allowance = token_contract.functions.allowance(account.address, PANCAKE_ROUTER_ADDRESS).call()
                if allowance < amount_in:
                    approve_tx = token_contract.functions.approve(
                        PANCAKE_ROUTER_ADDRESS,
                        2**256 - 1  # 最大值
                    ).build_transaction({
                        'from': account.address,
                        'gas': 100000,
                        'gasPrice': w3.eth.gas_price,
                        'nonce': nonce,
                        'chainId': 97
                    })
                    
                    # 签名并发送授权交易
                    signed_approve_tx = w3.eth.account.sign_transaction(approve_tx, private_key)
                    approve_tx_hash = w3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
                    w3.eth.wait_for_transaction_receipt(approve_tx_hash)
                    print("代币授权成功")
                    nonce += 1
                else:
                    print("已有足够的授权额度")
                    print("代币授权成功")

                # 计算预期输出
                path = [input_token, output_token]
                amounts_out = router_contract.functions.getAmountsOut(amount_in, path).call()
                amount_out_min = int(amounts_out[1] * 0.9)  # 允许 10% 的滑点
                print(f"预期输出金额: {w3.from_wei(amounts_out[1], 'ether')} BNB")
                print(f"最小输出金额: {w3.from_wei(amount_out_min, 'ether')} BNB")

                # 构建交易
                transaction = router_contract.functions.swapExactTokensForETH(
                    amount_in,
                    amount_out_min,
                    path,
                    account.address,
                    deadline
                ).build_transaction({
                    'from': account.address,
                    'value': 0,
                    'gas': 300000,  # gas 限制
                    'gasPrice': w3.eth.gas_price,  # 使用当前 gas 价格
                    'nonce': nonce,
                    'chainId': 97  # BSC 测试网的 chainId
                })

            elif trade_type == "TOKEN_TO_TOKEN":
                # 检查代币余额和授权
                token_contract = w3.eth.contract(address=input_token, abi=erc20_abi)
                token_balance = token_contract.functions.balanceOf(account.address).call()
                print(f"当前ETH余额: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} ETH")
                print(f"当前代币余额: {w3.from_wei(token_balance, 'ether')} Token")

                # 检查并授权代币
                print("正在授权代币...")
                allowance = token_contract.functions.allowance(account.address, PANCAKE_ROUTER_ADDRESS).call()
                if allowance < amount_in:
                    approve_tx = token_contract.functions.approve(
                        PANCAKE_ROUTER_ADDRESS,
                        2**256 - 1  # 最大值
                    ).build_transaction({
                        'from': account.address,
                        'gas': 100000,
                        'gasPrice': w3.eth.gas_price,
                        'nonce': nonce,
                        'chainId': 97
                    })
                    
                    # 签名并发送授权交易
                    signed_approve_tx = w3.eth.account.sign_transaction(approve_tx, private_key)
                    approve_tx_hash = w3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
                    w3.eth.wait_for_transaction_receipt(approve_tx_hash)
                    print("代币授权成功")
                    nonce += 1
                else:
                    print("已有足够的授权额度")
                    print("代币授权成功")

                # 计算预期输出
                path = [input_token, output_token]
                amounts_out = router_contract.functions.getAmountsOut(amount_in, path).call()
                amount_out_min = int(amounts_out[1] * 0.9)  # 允许 10% 的滑点
                print(f"预期输出金额: {w3.from_wei(amounts_out[1], 'ether')} Token")
                print(f"最小输出金额: {w3.from_wei(amount_out_min, 'ether')} Token")

                # 构建交易
                transaction = router_contract.functions.swapExactTokensForTokens(
                    amount_in,
                    amount_out_min,
                    path,
                    account.address,
                    deadline
                ).build_transaction({
                    'from': account.address,
                    'value': 0,
                    'gas': 300000,  # gas 限制
                    'gasPrice': w3.eth.gas_price,  # 使用当前 gas 价格
                    'nonce': nonce,
                    'chainId': 97  # BSC 测试网的 chainId
                })

            else:
                return f"不支持的交易类型: {trade_type}"

            # 签名并发送交易
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"交易已发送，等待确认... Hash: {tx_hash.hex()}")
            
            # 等待交易确认
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # 检查交易状态
            if tx_receipt['status'] == 1:
                return f"Successfully executed {trade_type} trade. Transaction hash: {tx_hash.hex()}"
            else:
                return f"Transaction failed. Transaction hash: {tx_hash.hex()}"

        except Exception as e:
            return f"Error executing trade: {e}"
