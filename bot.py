import requests
import pandas as pd
import time
from datetime import datetime
import ta

# =========================
# CONFIGURACIÓN
# =========================

TOKEN = "8651397125:AAHHpJQ6j0_GNQ8HCTBPtHgitD5zBrfgz84"
CHAT_ID = "8651397125"

PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "ADAUSDT"
]

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

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message
        })
    except:
        print("Error enviando señal")

# =========================
# OBTENER DATOS
# =========================

def get_data(pair):

    url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval=1m&limit=200"

    try:

        response = requests.get(url, timeout=10)

        data = response.json()

        if not isinstance(data, list):
            print("Error API:", data)
            return None

        df = pd.DataFrame(data)

        if df.empty:
            return None

        df = df.iloc[:,0:6]

        df.columns = [
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]

        df = df[["open","high","low","close"]]

        df = df.astype(float)

        return df

    except Exception as e:

        print("Error obteniendo datos:", e)

        return None

# =========================
# ANALISIS DEL MERCADO
# =========================

def analyze(pair):

    df = get_data(pair)

    if df is None:
        return

    if len(df) < 50:
        return

    try:

        df["rsi"] = ta.momentum.RSIIndicator(df["close"],14).rsi()

        bb = ta.volatility.BollingerBands(df["close"],20)

        df["bb_high"] = bb.bollinger_hband()
        df["bb_low"] = bb.bollinger_lband()

        ema = ta.trend.EMAIndicator(df["close"],50)

        df["ema"] = ema.ema_indicator()

        last = df.iloc[-1]

        open_price = last["open"]
        close_price = last["close"]
        high_price = last["high"]
        low_price = last["low"]

        body = abs(close_price - open_price)

        wick_up = high_price - max(close_price, open_price)

        wick_down = min(close_price, open_price) - low_price

        # ======================
        # SEÑAL CALL
        # ======================

        if (
            close_price < last["bb_low"]
            and last["rsi"] < 30
            and wick_down > body
        ):

            send_signal(pair, "CALL")

        # ======================
        # SEÑAL PUT
        # ======================

        if (
            close_price > last["bb_high"]
            and last["rsi"] > 70
            and wick_up > body
        ):

            send_signal(pair, "PUT")

    except Exception as e:

        print("Error en análisis:", e)

# =========================
# LOOP PRINCIPAL
# =========================

print("BOT DE SEÑALES INICIADO")

while True:

    try:

        for pair in PAIRS:

            analyze(pair)

        time.sleep(60)

    except Exception as e:

        print("Error general:", e)

        time.sleep(60) 
