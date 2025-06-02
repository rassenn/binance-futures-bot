
import os
import time
import numpy as np
import pandas as pd
from binance.client import Client
from binance.enums import *
import ta

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
client = Client(API_KEY, API_SECRET, testnet=True)

SYMBOL = 'BTCUSDT'
INTERVAL = '5m'
QUANTIDADE = 0.001
STOP_LOSS_PERCENT = 0.5
TAKE_PROFIT_PERCENT = 1

def get_data(symbol, interval, limit=100):
    df = pd.DataFrame(client.futures_klines(symbol=symbol, interval=interval, limit=limit))
    df.columns = ['timestamp','open','high','low','close','volume',
                  'close_time','quote_asset_volume','number_of_trades',
                  'taker_buy_base','taker_buy_quote','ignore']
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    return df

def sinal_trade(df):
    df['ema'] = ta.trend.ema_indicator(df['close'], window=20)
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=10).rsi()
    volume_threshold = np.percentile(df['volume'], 60)
    ultimo = df.iloc[-1]
    penultimo = df.iloc[-2]
    if (
        ultimo['rsi'] < 30 and
        penultimo['close'] < penultimo['ema'] and
        ultimo['close'] > ultimo['ema'] and
        ultimo['volume'] > volume_threshold
    ):
        return 'buy'
    return None

def executar_ordem(direcao):
    preco = float(client.futures_symbol_ticker(symbol=SYMBOL)['price'])
    order = client.futures_create_order(
        symbol=SYMBOL,
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        quantity=QUANTIDADE
    )
    print(f"Ordem executada: BUY @ {preco}")

while True:
    try:
        df = get_data(SYMBOL, INTERVAL)
        sinal = sinal_trade(df)
        if sinal:
            executar_ordem(sinal)
        else:
            print("Sem sinal. Aguardando próximo candle...")
    except Exception as e:
        print(f"Erro: {e}")
    time.sleep(300)
