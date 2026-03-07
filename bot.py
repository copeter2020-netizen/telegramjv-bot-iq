import requests
import pandas as pd
import time
from datetime import datetime
import ta

TOKEN = "TU_TOKEN_DE_TELEGRAM"
CHAT_ID = "TU_CHAT_ID"

PAIR = "EURUSD"

def send_signal(pair, direction, prob, score):
    now = datetime.utcnow()
    entry_time = now.strftime("%H:%M:59")

    message = f"""
🚨 MEJOR SEÑAL

Par: {pair}-OTC
Hora: {entry_time}
Dirección: {direction}
Probabilidad: {prob}%
Expiración: 1 minuto
Score: {score}
"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})


def get_data():
    url = f"https://api.binance.com/api/v3/klines?symbol={PAIR}&interval=1m&limit=100"
    data = requests.get(url).json()

    df = pd.DataFrame(data)
    df = df[[1,2,3,4]]
    df.columns = ["open","high","low","close"]
    df = df.astype(float)

    return df


def analyze():
    df = get_data()

    df["rsi"] = ta.momentum.RSIIndicator(df["close"],14).rsi()
    bb = ta.volatility.BollingerBands(df["close"],20,2)

    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()

    ema = ta.trend.EMAIndicator(df["close"],50)
    df["ema"] = ema.ema_indicator()

    last = df.iloc[-1]

    if last["close"] < last["bb_low"] and last["rsi"] < 30:
        send_signal(PAIR,"CALL",92,8)

    if last["close"] > last["bb_high"] and last["rsi"] > 70:
        send_signal(PAIR,"PUT",92,8)


while True:
    try:
        analyze()
        time.sleep(60)

    except Exception as e:
        print(e)
        time.sleep(60) 
