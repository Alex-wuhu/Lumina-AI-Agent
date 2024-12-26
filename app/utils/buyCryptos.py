from web3 import Web3
from eth_account import Account
import time
import json

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
        self.input_token = Web3.to_checksum_address(input_token) if input_token else None
        self.output_token = Web3.to_checksum_address(output_token) if output_token else None
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
        print(f"使用账户地址: {self.account.address}")

    def check_balances(self):
        """检查用户余额"""
        eth_balance = self.agent_contract.functions.getETHBalance().call({'from': self.account.address})
        print(f"合约中的ETH余额: {self.w3.from_wei(eth_balance, 'ether')} ETH")

        # 检查账户的 BNB 余额
        account_balance = self.w3.eth.get_balance(self.account.address)
        print(f"账户BNB余额: {self.w3.from_wei(account_balance, 'ether')} BNB")

        if self.trade_type != 'ETH_TO_TOKEN':
            token_balance = self.agent_contract.functions.getTokenBalance(self.input_token).call(
                {'from': self.account.address})
            print(f"合约中的代币余额: {self.w3.from_wei(token_balance, 'ether')} Token")

            # 检查账户的代币余额
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                }
            ]
            token_contract = self.w3.eth.contract(address=self.input_token, abi=erc20_abi)
            account_token_balance = token_contract.functions.balanceOf(self.account.address).call()
            print(f"账户代币余额: {self.w3.from_wei(account_token_balance, 'ether')} Token")

            return token_balance >= self.w3.to_wei(self.amount, 'ether')

        return eth_balance >= self.w3.to_wei(self.amount, 'ether')

    def approve_token(self, token_address, amount):
        """授权代币"""
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
            return True

        except Exception as e:
            print(f"Error approving tokens: {e}")
            return False

    def execute_trade(self):
        """执行交易"""
        try:
            # 检查余额
            if not self.check_balances():
                return "余额不足"

            # 如果是代币交易，需要先授权
            if self.trade_type in ['TOKEN_TO_ETH', 'TOKEN_TO_TOKEN']:
                if not self.approve_token(self.input_token, self.amount):
                    return "代币授权失败"

            # 准备通用参数
            amount_in = self.w3.to_wei(self.amount, 'ether')
            deadline = int(time.time()) + 600  # 10分钟后过期
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # 根据交易类型设置路径
            if self.trade_type == "ETH_TO_TOKEN":
                path = [self.WBNB, self.output_token]
            else:
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
                    'value': amount_in,  # 需要发送 ETH 给合约，合约再转发给 PancakeRouter
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
