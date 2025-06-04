import os
import time
import threading
from binance.client import Client
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import requests
import pandas as pd

# Configurações
PAIRS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'OPUSDT', 'DOGEUSDT']
TRADE_AMOUNT = 10.0
RSI_PERIOD = 14
SMA_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = Client(API_KEY, API_SECRET)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except:
        pass

def fetch_klines(symbol):
    klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=100)
    closes = [float(k[4]) for k in klines]
    return closes

def analyze(symbol):
    closes = fetch_klines(symbol)
    if len(closes) < RSI_PERIOD:
        return None

    rsi = RSIIndicator(close=pd.Series(closes), window=RSI_PERIOD).rsi().iloc[-1]
    sma = SMAIndicator(close=pd.Series(closes), window=SMA_PERIOD).sma_indicator().iloc[-1]
    last_price = closes[-1]

    if rsi < RSI_OVERSOLD and last_price > sma:
        return "BUY"
    elif rsi > RSI_OVERBOUGHT and last_price < sma:
        return "SELL"
    return None

def execute_trade(symbol, side):
    try:
        price = float(client.get_symbol_ticker(symbol=symbol)["price"])
        quantity = round(TRADE_AMOUNT / price, 3)
        order = client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_BUY if side == "BUY" else Client.SIDE_SELL,
            type="MARKET",
            quantity=quantity
        )
        send_telegram_message(f"✅ {side} em {symbol} executado.")
Preço: {price}")
    except Exception as e:
        send_telegram_message(f"⚠️ Erro ao operar {symbol}: {e}")

def monitor_pair(symbol):
    while True:
        signal = analyze(symbol)
        if signal:
            execute_trade(symbol, signal)
        time.sleep(60)

def main():
    threads = []
    for pair in PAIRS:
        t = threading.Thread(target=monitor_pair, args=(pair,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
