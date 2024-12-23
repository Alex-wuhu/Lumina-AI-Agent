from app.utils.buyCryptos import BuyCryptos


def buyCryptos(trade_type: str, input_token: str, output_token: str, amount: float) -> str:

    if input_token == "ETH":
        input = "0xeD24FC36d5Ee211Ea25A80239Fb84Cfd80f12Ee"
    if input_token == "BNB":
        input = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"
    if output_token == "ETH":
        output = "0xeD24FC36d5Ee211Ea25A80239Fb84Cfd80f12Ee"
    if output_token == "BNB":
        output = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"

    trade = BuyCryptos(
        trade_type = trade_type,
        input_token = input,
        output_token = output,
        amount = amount
    )

    # 执行交易
    result = trade.execute_trade()
    print(f"交易结果: {result}")
    print(f"{trade_type} {input_token} {output_token} accept")
    return f"{amount} done sucess"