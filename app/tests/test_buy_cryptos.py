import sys
import os
from web3 import Web3
import json

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
        output_token="0x0841e381a6363e6e7fbd742407b5749fc5e73083",  # BUSD
        amount=0.001  # BNB
    )
    
    # 检查余额
    trade.check_balances()
    
    # 先存入 ETH
    result = trade.deposit_eth(0.001)
    if not result:
        print("存入 ETH 失败")
        return
        
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

def test_tbnb_to_wbnb():
    """测试用测试网tBNB兑换wBNB"""
    print("\n=== 测试用tBNB兑换wBNB ===")
    
    # 创建交易实例
    amount = 0.01  # 兑换0.01个代币
    amount_wei = Web3.to_wei(amount, 'ether')
    wbnb_address = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"
    
    trade = BuyCryptos(
        trade_type="ETH_TO_TOKEN",
        input_token=None,  # ETH_TO_TOKEN类型不需要input_token
        output_token=wbnb_address,
        amount=amount
    )
    
    # 检查余额
    trade.check_balances()
    
    # 先存入ETH到合约
    result = trade.deposit_eth(amount)
    print(f"存款结果: {result}")
    trade.check_balances()
    
    # 执行兑换
    result = trade.execute_trade()
    print(f"兑换结果: {result}")
    trade.check_balances()
    
    # 检查WBNB合约的余额
    with open("/Users/k/PycharmProjects/Lumina-AI-Agent/app/abis/erc20_abi.json", "r") as f:
        erc20_abi = json.load(f)
    wbnb_contract = trade.w3.eth.contract(address=wbnb_address, abi=erc20_abi)
    wbnb_balance = wbnb_contract.functions.balanceOf(trade.account.address).call()
    print(f"\nWBNB合约中的余额: {wbnb_balance / 10**18} WBNB")
    
    # 把WBNB存入合约
    print("\n把WBNB存入合约...")
    trade.deposit_token(wbnb_address, amount_wei)
    trade.check_balances()

def test_eth_to_wbnb():
    """测试用ETH换wBNB"""
    print("\n=== 测试用ETH换wBNB ===")
    
    # 创建交易实例
    trade = BuyCryptos(
        trade_type="ETH_TO_TOKEN",
        input_token=None,  # ETH_TO_TOKEN类型不需要input_token
        output_token="0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",  # WBNB地址
        amount=0.01  # 兑换的ETH数量
    )
    
    # 检查余额
    trade.check_balances()
    
    # 存入ETH
    result = trade.deposit_eth(0.01)
    if not result:
        print("存入 ETH 失败")
        return
        
    # 执行兑换
    result = trade.execute_trade()
    print(f"兑换结果: {result}")
    
    # 再次检查余额
    trade.check_balances()

def test_deposit_wbnb():
    """测试存入WBNB到合约"""
    print("\n=== 测试存入WBNB到合约 ===")
    
    # 创建交易实例
    amount = 0.01  # 存入0.01个代币
    wbnb_address = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"
    
    trade = BuyCryptos(
        trade_type="TOKEN_TO_ETH",  # 这里的trade_type不重要，因为我们只是用来存款
        input_token=wbnb_address,
        output_token=None,
        amount=amount
    )
    
    # 检查余额
    trade.check_balances()
    
    # 存入WBNB到合约
    print("\n把WBNB存入合约...")
    result = trade.deposit_token(wbnb_address, amount)  # 直接使用amount，不转换为wei
    if result:
        print("WBNB存入成功")
    else:
        print("WBNB存入失败")
    
    # 再次检查余额
    trade.check_balances()

def test_wbnb_to_eth():
    """测试用wBNB换回ETH"""
    print("\n=== 测试用wBNB换回ETH ===")
    
    # 先运行test_tbnb_to_wbnb来获取WBNB
    #test_tbnb_to_wbnb()
    
    # 创建交易实例
    amount = 0.01  # 兑换0.01个代币
    amount_wei = Web3.to_wei(amount, 'ether')
    wbnb_address = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"
    
    trade = BuyCryptos(
        trade_type="TOKEN_TO_ETH",
        input_token=wbnb_address,
        output_token=None,  # TOKEN_TO_ETH 不需要output_token
        amount=amount
    )
    
    # 检查余额
    trade.check_balances()
    
    # 先从合约中提取WBNB
    #print("\n提取WBNB从合约到账户...")
    #trade.withdraw_token(wbnb_address, amount_wei)
    #trade.check_balances()
    
    # 授权代币
    trade.approve_token(wbnb_address, amount_wei)
    
    # 执行兑换
    result = trade.execute_trade()
    print(f"兑换结果: {result}")
    
    # 再次检查余额
    trade.check_balances()

if __name__ == "__main__":
    print("开始测试智能合约交互...\n")
    #test_tbnb_to_wbnb()
    #test_eth_to_wbnb()
    #test_deposit_wbnb()
    test_wbnb_to_eth()
