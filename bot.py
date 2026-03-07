import time
import requests
import pandas as pd
from datetime import datetime
import ta
from iqoptionapi.stable_api import IQ_Option

# =========================
# CONFIGURACION
# =========================

IQ_EMAIL = "TU_EMAIL"
IQ_PASSWORD = "TU_PASSWORD"

TOKEN = "TU_TOKEN_TELEGRAM"
CHAT_ID = "TU_CHAT_ID"

# =========================
# CONECTAR IQ OPTION
# =========================

def connect_iq():

    while True:

        try:

            print("Conectando a IQ Option...")

            iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)

            iq.connect()

            if iq.check_connect():

                print("Conectado correctamente")

                return iq

            else:

                print("Error de conexión, reintentando...")

                time.sleep(10)

        except Exception as e:

            print("Error:", e)

            time.sleep(10)

Iq = connect_iq()

# =========================
# TELEGRAM
# =========================

def send_signal(pair, direction):

    entry = datetime.utcnow().strftime("%H:%M:59")

    message = f"""
🚨 MEJOR SEÑAL

Par: {pair}
Hora: {entry}
Dirección: {direction}
Expiración: 1 minuto
"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:

        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message
        })

    except:

        print("Error enviando señal")

# =========================
# OBTENER PARES OTC
# =========================

def get_otc_pairs():

    pairs = []

    assets = Iq.get_all_open_time()

    for asset in assets["digital"]:

        if "OTC" in asset:

            if assets["digital"][asset]["open"]:

                pairs.append(asset)

    return pairs

# =========================
# OBTENER VELAS
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

    body = abs(last["close"] - last["open"])

    wick_up = last["high"] - max(last["close"], last["open"])

    wick_down = min(last["close"], last["open"]) - last["low"]

    # CALL

    if last["close"] < last["bb_low"] and last["rsi"] < 30 and wick_down > body:

        send_signal(pair,"CALL")

    # PUT

    if last["close"] > last["bb_high"] and last["rsi"] > 70 and wick_up > body:

        send_signal(pair,"PUT")

# =========================
# LOOP
# =========================

print("BOT OTC INICIADO")

while True:

    try:

        pairs = get_otc_pairs()

        print("Pares OTC activos:", pairs)

        for pair in pairs:

            analyze(pair)

        time.sleep(60)

    except Exception as e:

        print("Error:", e)

        time.sleep(10) 
