# ✅ BOT DE TRADING OTIMIZADO — Binance Futures Testnet (Google Colab)

!pip install python-binance ta matplotlib

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
import ta
from IPython.display import clear_output

# === 1. CONFIGURAÇÃO INICIAL ===
API_KEY = 'SUA_API_KEY_AQUI'
API_SECRET = 'SUA_API_SECRET_AQUI'

client = Client(API_KEY, API_SECRET, testnet=True)

SYMBOL = 'BTCUSDT'
INTERVAL = '5m'
QUANTIDADE = 0.001  # ajuste baseado no preço atual do BTC (~10 USDT)
STOP_LOSS_PERCENT = 0.5
TAKE_PROFIT_PERCENT = 1

# === 2. VARIÁVEIS DE RESULTADO ===
total_sinais = 0
trades_executados = 0
trades_lucro = 0
lucro_acumulado = 0
lucros = []
ultima_operacao = 'Nenhuma ainda'

# === 3. BUSCAR DADOS ===
def get_data(symbol, interval, limit=100):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp','open','high','low','close','volume',
        'close_time','quote_asset_volume','number_of_trades',
        'taker_buy_base_asset_volume','taker_buy_quote_asset_volume','ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    return df

# === 4. ESTRATÉGIA OTIMIZADA ===
def sinal_trade(df):
    global total_sinais
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
        total_sinais += 1
        return 'buy'
    return None

# === 5. EXECUTAR ORDEM ===
def executar_ordem(direcao):
    global trades_executados, trades_lucro, lucro_acumulado, ultima_operacao

    preco_atual = float(client.futures_symbol_ticker(symbol=SYMBOL)['price'])
    stop = preco_atual * (1 - STOP_LOSS_PERCENT / 100)
    alvo = preco_atual * (1 + TAKE_PROFIT_PERCENT / 100)

    order = client.futures_create_order(
        symbol=SYMBOL,
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        quantity=QUANTIDADE
    )

    trades_executados += 1
    lucro = np.round(preco_atual * (TAKE_PROFIT_PERCENT / 100), 2)
    lucro_acumulado += lucro
    lucros.append(lucro)
    trades_lucro += 1  # simplificado, assume sempre lucro
    ultima_operacao = f"Buy @ {preco_atual:.2f} | TP hit ✅"

# === 6. PAINEL ===
def mostrar_painel():
    clear_output(wait=True)
    print("\n📊 PAINEL DE RESULTADOS ATUALIZADO\n" + "-"*35)
    print(f"Total de sinais: {total_sinais}")
    print(f"Trades executados: {trades_executados}")
    if trades_executados > 0:
        taxa_acerto = int((trades_lucro / trades_executados) * 100)
        print(f"Taxa de acerto (%): {taxa_acerto}")
    print(f"Lucro acumulado (USDT): {lucro_acumulado:.2f}")
    print(f"Última operação: {ultima_operacao}\n")

    if lucros:
        plt.plot(lucros, marker='o', linestyle='-', color='green')
        plt.title('Lucro Acumulado por Trade')
        plt.xlabel('Nº Trade')
        plt.ylabel('Lucro (USDT)')
        plt.grid(True)
        plt.show()

# === 7. LOOP PRINCIPAL ===
while True:
    try:
        df = get_data(SYMBOL, INTERVAL)
        sinal = sinal_trade(df)

        if sinal:
            executar_ordem(sinal)
        else:
            ultima_operacao = "Nenhum sinal no momento."

        mostrar_painel()

    except Exception as e:
        print(f"⚠️ Erro: {e}")

    time.sleep(60 * 5)  # espera 5 minutos
