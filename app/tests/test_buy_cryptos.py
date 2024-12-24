import sys
import os
from web3 import Web3

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.buyCryptos import BuyCryptos

def test_1_bnb_to_token():
    """测试用BNB购买代币"""
    print("\n=== 测试用BNB购买代币 ===")
    
    # 创建交易实例
    trade = BuyCryptos(
        trade_type="ETH_TO_TOKEN",
        input_token="0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",  # WBNB
        output_token="0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee",  # BUSD
        amount=0.001  # BNB
    )
    
    # 打印交易参数
    print(f"交易类型: {trade.trade_type}")
    print(f"输入代币: {trade.input_token}")
    print(f"输出代币: {trade.output_token}")
    print(f"数量: {trade.amount} BNB")
    
    # 执行交易
    result = trade.execute_trade()
    print(f"交易结果: {result}")

def test_2_token_to_bnb():
    """测试代币卖回BNB"""
    print("\n=== 测试代币卖回BNB ===")
    
    # 创建交易实例
    trade = BuyCryptos(
        trade_type="TOKEN_TO_ETH",
        input_token="0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee",  # BUSD
        output_token="0xa1bd0b49b57141ffa0a3e94d4adf953716e28b1c",  # WBNB
        amount=0.001  # Token
    )
    
    # 打印交易参数
    print(f"交易类型: {trade.trade_type}")
    print(f"输入代币: {trade.input_token}")
    print(f"输出代币: {trade.output_token}")
    print(f"数量: {trade.amount} Token")
    
    # 执行交易
    result = trade.execute_trade()
    print(f"交易结果: {result}")

def test_3_get_token_balance():
    print("\n=== 测试查询代币余额 ===")
    # 创建交易实例
    trade = BuyCryptos(
        trade_type="TOKEN_TO_ETH",
        input_token="0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee",  # BUSD
        output_token="0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",  # WBNB
        amount=0.001  # Token
    )
    
    # 查询 BUSD 代币余额
    balance = trade.agent_contract.functions.getTokenBalance(trade.input_token).call({'from': trade.account.address})
    print(f"账户 {trade.account.address} 的 BUSD 余额: {Web3.from_wei(balance, 'ether')} BUSD")

def test_token_to_token():
    """测试代币互换"""
    print("\n=== 测试代币互换 ===")
    
    # 创建交易实例
    trade = BuyCryptos(
        trade_type="TOKEN_TO_TOKEN",
        input_token="0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee",  # BUSD
        output_token="0x78867BbEeF44f2326bF8DDd1941a4439382EF2A7",  # BUSD
        amount=0.001  # Token
    )
    
    # 打印交易参数
    print(f"交易类型: {trade.trade_type}")
    print(f"输入代币: {trade.input_token}")
    print(f"输出代币: {trade.output_token}")
    print(f"数量: {trade.amount} Token")
    
    # 执行交易
    result = trade.execute_trade()
    print(f"交易结果: {result}")

if __name__ == "__main__":
    print("开始测试智能合约交互...\n")
    test_1_bnb_to_token()
    test_2_token_to_bnb()
    test_3_get_token_balance()
