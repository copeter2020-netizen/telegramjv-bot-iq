 import requests
import pandas as pd
import time
from datetime import datetime
import ta

TOKEN = "8651397125:AAHHpJQ6j0_GNQ8HCTBPtHgitD5zBrfgz84"
CHAT_ID = "8651397125"

API_KEY = "TU_API_KEY_TWELVEDATA"

PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "AUD/USD"
]

# =========================
# TELEGRAM
# =========================

def send_signal(pair, direction):

    now = datetime.utcnow()
    entry = now.strftime("%H:%M:59")

    msg = f"""
🚨 MEJOR SEÑAL

Par: {pair}
Hora: {entry}
Dirección: {direction}
Expiración: 1 minuto
"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# =========================
# OBTENER DATOS
# =========================

def get_data(pair):

    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=1min&outputsize=200&apikey={API_KEY}"

    r = requests.get(url)
    data = r.json()

    if "values" not in data:
        print("Error API:", data)
        return None

    df = pd.DataFrame(data["values"])

    df = df[["open","high","low","close"]]

    df = df.astype(float)

    df = df[::-1]

    return df

# =========================
# ANALISIS
# =========================

def analyze(pair):

    df = get_data(pair)

    if df is None:
        return

    df["rsi"] = ta.momentum.RSIIndicator(df["close"],14).rsi()

    bb = ta.volatility.BollingerBands(df["close"],20)

    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()

    last = df.iloc[-1]

    body = abs(last["close"] - last["open"])

    wick_up = last["high"] - max(last["close"], last["open"])

    wick_down = min(last["close"], last["open"]) - last["low"]

    # CALL
    if last["close"] < last["bb_low"] and last["rsi"] < 30 and wick_down > body:
        send_signal(pair,"CALL")

    # PUT
    if last["close"] > last["bb_high"] and last["rsi"] > 70 and wick_up > body:
        send_signal(pair,"PUT")

print("BOT DE SEÑALES INICIADO")

while True:

    try:

        for pair in PAIRS:

            analyze(pair)

        time.sleep(60)

    except Exception as e:

        print("Error:", e)

        time.sleep(60)      
