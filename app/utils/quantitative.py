import requests
import pandas as pd
def query_eth_rsi():
    timeinterval = 5
    
    url = 'https://api.binance.com/api/v3/klines?symbol=ETHUSDT'+'&interval='+str(timeinterval)+'m'+'&limit=100'
    data = requests.get(url).json()        
    D = pd.DataFrame(data)
    D.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
                 'taker_base_vol', 'taker_quote_vol', 'is_best_match']
    period=14
    df=D
    df['close'] = df['close'].astype(float)
    df2=df['close'].to_numpy()
    df2 = pd.DataFrame(df2, columns = ['close'])
    delta = df2.diff()
    
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    
    _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()
    
    RS = _gain / _loss
    
    
    rsi=100 - (100 / (1 + RS))  
    rsi=rsi['close'].iloc[-1]
    rsi=round(rsi,1)

    return rsi


def query_eth_indicators():
    endpoint = "https://api.binance.com/api/v3/ticker?symbol=ETHUSDT&&windowSize=1d"
    response = requests.get(endpoint)
    rsi = query_eth_rsi()
    data = response.json()
    result = {
        "lastPrice ETH/USDT": data["lastPrice"],
        "1 day ETH/USDT VWAP": data["weightedAvgPrice"],
        "14 days ETH/USDT rsi" : rsi
    }
    print(result)
    return result

