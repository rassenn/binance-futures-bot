import os
import time
import requests
import logging
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

# Configurações
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
interval = Client.KLINE_INTERVAL_5MINUTE
limit = 100
rsi_period = 14
sma_period = 14
rsi_overbought = 70
rsi_oversold = 30
trade_quantity = 10  # USDT por operação

# Autenticação
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

client = Client(api_key, api_secret)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {"chat_id": telegram_chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Erro ao enviar mensagem Telegram: {e}")

def get_klines(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        close_prices = [float(k[4]) for k in klines]
        return close_prices
    except Exception as e:
        send_telegram_message(f"Erro ao obter dados de {symbol}: {e}")
        return []

def analyze(symbol):
    closes = get_klines(symbol)
    if not closes or len(closes) < rsi_period:
        return None

    import pandas as pd
    rsi = RSIIndicator(pd.Series(closes), window=rsi_period).rsi().iloc[-1]
    sma = SMAIndicator(pd.Series(closes), window=sma_period).sma_indicator().iloc[-1]
    price = closes[-1]

    if rsi < rsi_oversold and price > sma:
        return "BUY", price
    elif rsi > rsi_overbought and price < sma:
        return "SELL", price
    return None

def execute_trade(symbol, side):
    try:
        order = client.create_order(
            symbol=symbol,
            side=SIDE_BUY if side == "BUY" else SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quoteOrderQty=trade_quantity
        )
        price = order['fills'][0]['price']
        send_telegram_message(f"✅ {side} em {symbol} executado.\nPreço: {price}")
    except Exception as e:
        send_telegram_message(f"Erro ao executar {side} em {symbol}: {e}")

def run_bot():
    while True:
        for symbol in symbols:
            signal = analyze(symbol)
            if signal:
                side, price = signal
                execute_trade(symbol, side)
            time.sleep(1)
        time.sleep(60)

if __name__ == "__main__":
    run_bot()
