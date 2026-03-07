 import requests
import time
import requests
import pandas as pd
from datetime import datetime
import ta

from iqoptionapi.stable_api import IQ_Option

# =========================
# CONFIGURACION
# =========================

IQ_EMAIL = "TU_EMAIL_IQOPTION"
IQ_PASSWORD = "TU_PASSWORD_IQOPTION"

TOKEN = "TU_TOKEN_TELEGRAM"
CHAT_ID = "TU_CHAT_ID"

PAIRS = [
    "EURUSD-OTC",
    "GBPUSD-OTC",
    "AUDCAD-OTC",
    "EURGBP-OTC"
]

# =========================
# CONECTAR IQ OPTION
# =========================

print("Conectando a IQ Option...")

Iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
Iq.connect()

if Iq.check_connect():
    print("Conectado correctamente")
else:
    print("Error conectando")
    exit()

# =========================
# TELEGRAM
# =========================

def send_signal(pair, direction):

    now = datetime.utcnow()
    entry = now.strftime("%H:%M:59")

    message = f"""
🚨 MEJOR SEÑAL

Par: {pair}
Hora: {entry}
Dirección: {direction}
Expiración: 1 minuto
"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

# =========================
# OBTENER VELAS OTC
# =========================

def get_data(pair):

    candles = Iq.get_candles(pair, 60, 200, time.time())

    df = pd.DataFrame(candles)

    df = df[["open","max","min","close"]]

    df.columns = ["open","high","low","close"]

    df = df.astype(float)

    return df

# =========================
# ANALISIS
# =========================

def analyze(pair):

    df = get_data(pair)

    if len(df) < 50:
        return

    df["rsi"] = ta.momentum.RSIIndicator(df["close"],14).rsi()

    bb = ta.volatility.BollingerBands(df["close"],20)

    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()

    last = df.iloc[-1]

    open_price = last["open"]
    close_price = last["close"]
    high_price = last["high"]
    low_price = last["low"]

    body = abs(close_price - open_price)

    wick_up = high_price - max(close_price, open_price)
    wick_down = min(close_price, open_price) - low_price

    # CALL
    if close_price < last["bb_low"] and last["rsi"] < 30 and wick_down > body:
        send_signal(pair,"CALL")

    # PUT
    if close_price > last["bb_high"] and last["rsi"] > 70 and wick_up > body:
        send_signal(pair,"PUT")

# =========================
# LOOP
# =========================

print("BOT OTC INICIADO")

while True:

    try:

        for pair in PAIRS:

            analyze(pair)

        time.sleep(60)

    except Exception as e:

        print("Error:", e)
        time.sleep(60) 
