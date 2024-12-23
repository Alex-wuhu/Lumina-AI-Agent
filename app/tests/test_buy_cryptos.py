import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.tools import BuyCryptos

def test_bnb_to_token():
    """测试用BNB购买代币"""
    print("\n=== 测试用BNB购买代币 ===")
    
    # 创建交易实例
    trade = BuyCryptos(
        trade_type="ETH_TO_TOKEN",
        input_token="0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",  # WBNB
        output_token="0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee",  # BUSD
        amount=0.005  # BNB
    )
    
    # 打印交易参数
    print(f"交易类型: {trade.trade_type}")
    print(f"输入代币: {trade.input_token}")
    print(f"输出代币: {trade.output_token}")
    print(f"数量: {trade.amount} BNB")
    
    # 执行交易
    result = trade.execute_trade()
    print(f"交易结果: {result}")

def test_token_to_bnb():
    """测试代币卖回BNB"""
    print("\n=== 测试代币卖回BNB ===")
    
    # 创建交易实例
    trade = BuyCryptos(
        trade_type="TOKEN_TO_ETH",
        input_token="0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee",  # BUSD
        output_token="0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",  # WBNB
        amount=0.005  # Token
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
    print("开始测试智能合约交互...")
    test_bnb_to_token()
    test_token_to_bnb()