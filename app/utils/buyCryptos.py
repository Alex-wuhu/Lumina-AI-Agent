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
        self.AGENT_ADDRESS = Web3.to_checksum_address("0x6739bb5aae6e8084cd4a119deb1707196c094064")  # 合约地址
        self.WBNB = Web3.to_checksum_address("0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd")

        # 加载合约 ABI
        with open("/Users/k/PycharmProjects/Lumina-AI-Agent/app/abis/agent_abi.json", "r") as f:
            self.agent_abi = json.load(f)

        # 创建合约实例
        self.agent_contract = self.w3.eth.contract(
            address=self.AGENT_ADDRESS,
            abi=self.agent_abi
        )

        # 创建账户
        self.private_key = ""
        self.account = Account.from_key(self.private_key)
        print(f"使用账户地址: {self.account.address}")

    def check_balances(self):
        """检查余额"""
        # 检查合约中的ETH余额
        eth_balance = self.w3.eth.get_balance(self.AGENT_ADDRESS)
        print(f"合约中的ETH余额: {eth_balance / 10**18:.2f} ETH")

        # 检查账户的ETH余额
        account_balance = self.w3.eth.get_balance(self.account.address)
        print(f"账户BNB余额: {account_balance / 10**18} BNB")

        # 如果有代币地址，检查代币余额
        if self.input_token or self.output_token:
            token_address = self.input_token if self.input_token else self.output_token
            # 创建代币合约实例
            with open("/Users/k/PycharmProjects/Lumina-AI-Agent/app/abis/erc20_abi.json", "r") as f:
                erc20_abi = json.load(f)
            token_contract = self.w3.eth.contract(address=token_address, abi=erc20_abi)

            # 检查合约中的代币余额
            contract_token_balance = token_contract.functions.balanceOf(self.AGENT_ADDRESS).call()
            print(f"合约中的代币余额: {contract_token_balance / 10**18} Token")

            # 检查用户在合约中的代币余额
            user_contract_token_balance = self.agent_contract.functions.userTokenBalances(
                self.account.address,
                token_address
            ).call()
            print(f"用户在合约中的代币余额: {user_contract_token_balance / 10**18} Token")

            # 检查账户的代币余额
            account_token_balance = token_contract.functions.balanceOf(self.account.address).call()
            print(f"账户代币余额: {account_token_balance / 10**18} Token")

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
                'gas': 50000,  # 降低gas限制
                'gasPrice': Web3.to_wei(1, 'gwei'),  # 设置较低的固定gas价格
                'nonce': nonce,
                'chainId': 97
            })

            # 签名并发送授权交易
            signed_approve_tx = self.w3.eth.account.sign_transaction(approve_tx, self.private_key)
            print("签名交易类型:", type(signed_approve_tx))
            print("签名交易内容:", signed_approve_tx)
            print("签名交易属性:", dir(signed_approve_tx))
            print("rawTransaction:", hasattr(signed_approve_tx, 'rawTransaction'))
            approve_tx_hash = self.w3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
            print(f"授权交易已发送，等待确认... Hash: {approve_tx_hash.hex()}")

            # 等待交易被确认
            receipt = self.w3.eth.wait_for_transaction_receipt(approve_tx_hash)
            if receipt['status'] != 1:
                print("授权交易失败")
                return False

            print("代币授权成功")

            # 等待几秒钟，确保nonce更新
            time.sleep(2)
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

            # 如果是TOKEN_TO_ETH，需要先把代币存入合约
            if self.trade_type == "TOKEN_TO_ETH":
                # 先存入代币到合约
                print("\n存入代币到合约...")
                self.deposit_token(self.input_token, amount_in)
                self.check_balances()

            # 根据交易类型设置路径
            if self.trade_type == "ETH_TO_TOKEN":
                path = [self.WBNB, self.output_token]
            elif self.trade_type == "TOKEN_TO_ETH":
                path = [self.input_token, self.WBNB]  # WBNB -> WBNB
            else:
                path = [self.input_token, self.output_token]

            # 根据交易类型执行不同的交易
            if self.trade_type == "ETH_TO_TOKEN":
                # 如果目标是WBNB，直接调用WBNB合约的deposit函数
                if self.output_token == self.WBNB:
                    # WBNB的ABI
                    wbnb_abi = [
                        {
                            "constant": False,
                            "inputs": [],
                            "name": "deposit",
                            "outputs": [],
                            "payable": True,
                            "stateMutability": "payable",
                            "type": "function"
                        }
                    ]
                    # 创建WBNB合约实例
                    wbnb_contract = self.w3.eth.contract(
                        address=self.WBNB,
                        abi=wbnb_abi
                    )

                    # 构建交易
                    transaction = wbnb_contract.functions.deposit().build_transaction({
                        'from': self.account.address,
                        'value': amount_in,
                        'gas': 50000,  # deposit函数的gas消耗很小
                        'gasPrice': Web3.to_wei(1, 'gwei'),
                        'nonce': self.w3.eth.get_transaction_count(self.account.address),
                        'chainId': 97
                    })
                else:
                    # 如果目标是其他token，使用PancakeRouter
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
                        'gas': 150000,
                        'gasPrice': Web3.to_wei(1, 'gwei'),
                        'nonce': self.w3.eth.get_transaction_count(self.account.address),
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
                    'gas': 150000,  # 降低gas限制
                    'gasPrice': Web3.to_wei(1, 'gwei'),  # 设置较低的固定gas价格
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
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
                    'gas': 150000,  # 降低gas限制
                    'gasPrice': Web3.to_wei(1, 'gwei'),  # 设置较低的固定gas价格
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                    'chainId': 97
                })

            else:
                return f"不支持的交易类型: {self.trade_type}"

            # 重新获取最新的nonce值
            transaction['nonce'] = self.w3.eth.get_transaction_count(self.account.address)

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

            # 重新获取最新的nonce值
            transaction['nonce'] = self.w3.eth.get_transaction_count(self.account.address)

            # 签名并发送交易
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"存款交易已发送，等待确认... Hash: {tx_hash.hex()}")
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print("存款成功")
            return True

        except Exception as e:
            print(f"Error depositing ETH: {e}")
            return False

    def deposit_token(self, token_address, amount):
        """存入代币"""
        try:
            amount_in_wei = self.w3.to_wei(amount, 'ether')

            # 创建 ERC20 合约实例
            with open("/Users/k/PycharmProjects/Lumina-AI-Agent/app/abis/erc20_abi.json", "r") as f:
                erc20_abi = json.load(f)
            token_contract = self.w3.eth.contract(address=token_address, abi=erc20_abi)

            # 授权代币
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            approve_tx = token_contract.functions.approve(
                self.AGENT_ADDRESS,
                amount_in_wei
            ).build_transaction({
                'from': self.account.address,
                'gas': 50000,  # 降低gas限制
                'gasPrice': Web3.to_wei(1, 'gwei'),  # 设置较低的固定gas价格
                'nonce': nonce,
                'chainId': 97
            })

            # 签名并发送授权交易
            signed_approve_tx = self.w3.eth.account.sign_transaction(approve_tx, self.private_key)
            print("签名交易类型:", type(signed_approve_tx))
            print("签名交易内容:", signed_approve_tx)
            print("签名交易属性:", dir(signed_approve_tx))
            print("rawTransaction:", hasattr(signed_approve_tx, 'rawTransaction'))
            approve_tx_hash = self.w3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
            print(f"授权交易已发送，等待确认... Hash: {approve_tx_hash.hex()}")

            # 等待交易被确认
            receipt = self.w3.eth.wait_for_transaction_receipt(approve_tx_hash)
            if receipt['status'] != 1:
                print("授权交易失败")
                return False

            print("代币授权成功")

            # 等待几秒钟，确保nonce更新
            time.sleep(2)

            # 存入代币
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # 如果是WBNB，使用depositWBNB函数
            if token_address == self.WBNB:
                transaction = self.agent_contract.functions.depositWBNB(
                    amount_in_wei
                ).build_transaction({
                    'from': self.account.address,
                    'gas': 100000,
                    'gasPrice': Web3.to_wei(1, 'gwei'),
                    'nonce': nonce,
                    'chainId': 97
                })
            else:
                transaction = self.agent_contract.functions.depositERC20(
                    token_address,
                    amount_in_wei
                ).build_transaction({
                    'from': self.account.address,
                    'gas': 100000,
                    'gasPrice': Web3.to_wei(1, 'gwei'),
                    'nonce': nonce,
                    'chainId': 97
                })

            # 重新获取最新的nonce值
            transaction['nonce'] = self.w3.eth.get_transaction_count(self.account.address)

            # 签名并发送存款交易
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"存款交易已发送，等待确认... Hash: {tx_hash.hex()}")

            # 等待交易确认
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # 检查交易是否成功
            if tx_receipt['status'] == 1:
                print("代币存款成功")
                return True
            else:
                print("代币存款失败")
                return False

        except Exception as e:
            print(f"Error depositing tokens: {e}")
            return False

    def withdraw_token(self, token_address, amount_wei):
        """从合约中提取代币

        Args:
            token_address: 代币地址
            amount_wei: 提取数量（以wei为单位）
        """
        nonce = self.w3.eth.get_transaction_count(self.account.address)

        # 构建交易
        transaction = self.agent_contract.functions.withdrawERC20(
            token_address,
            amount_wei
        ).build_transaction({
            'from': self.account.address,
            'gas': 100000,
            'gasPrice': Web3.to_wei(1, 'gwei'),
            'nonce': nonce,
            'chainId': 97
        })

        # 重新获取最新的nonce值
        transaction['nonce'] = self.w3.eth.get_transaction_count(self.account.address)

        # 签名交易
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
        
        # 发送交易
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"提取交易已发送，等待确认... Hash: {tx_hash.hex()}")
        
        # 等待交易确认
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # 检查交易是否成功
        if tx_receipt['status'] == 1:
            print("代币提取成功")
            return True
        else:
            print("代币提取失败")
            return False
