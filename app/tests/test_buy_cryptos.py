import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_eth_to_token():
    """测试用BNB购买代币"""
    try:
        from app.utils.tools import BuyCryptos
        
        # 测试参数
        trade_type = "ETH_TO_TOKEN"
        input_token = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"  # WBNB地址
        # BUSD测试网地址
        output_token = "0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee"  
        amount = 0.01  # 用0.01 BNB测试

        print("\n=== 测试用BNB购买代币 ===")
        print(f"交易类型: {trade_type}")
        print(f"输入代币: {input_token}")
        print(f"输出代币: {output_token}")
        print(f"数量: {amount} BNB")

        # 调用购买函数
        result = BuyCryptos(
            trade_type=trade_type,
            input_token=input_token,
            output_token=output_token,
            amount=amount
        )
        print(f"交易结果: {result}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_token_to_eth():
    """测试将代币换回BNB"""
    try:
        from app.utils.tools import BuyCryptos
        
        # 测试参数
        trade_type = "TOKEN_TO_ETH"
        # BUSD测试网地址
        input_token = "0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee"
        output_token = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"  # WBNB地址
        amount = 0.01  # 卖出0.01个代币

        print("\n=== 测试代币卖回BNB ===")
        print(f"交易类型: {trade_type}")
        print(f"输入代币: {input_token}")
        print(f"输出代币: {output_token}")
        print(f"数量: {amount} Token")

        # 调用卖出函数
        result = BuyCryptos(
            trade_type=trade_type,
            input_token=input_token,
            output_token=output_token,
            amount=amount
        )
        print(f"交易结果: {result}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_token_to_token():
    """测试代币互换"""
    try:
        from app.utils.tools import BuyCryptos
        
        # 测试参数
        trade_type = "TOKEN_TO_TOKEN"
        input_token = "0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee"  # BUSD测试网地址
        output_token = "0x78867BbEeF44f2326bF8DDd1941a4439382EF2A7"  # BUSD测试网地址
        amount = 0.01  # 交换0.01个代币

        print("\n=== 测试代币互换 ===")
        print(f"交易类型: {trade_type}")
        print(f"输入代币: {input_token}")
        print(f"输出代币: {output_token}")
        print(f"数量: {amount} Token")

        # 调用交换函数
        result = BuyCryptos(
            trade_type=trade_type,
            input_token=input_token,
            output_token=output_token,
            amount=amount
        )
        print(f"交易结果: {result}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    print("开始测试智能合约交互...")
    test_eth_to_token()
    test_token_to_eth()
    test_token_to_token()
