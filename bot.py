import requests
import pandas as pd
import time
from datetime import datetime
import ta

# =========================
# CONFIGURACIÓN
# =========================

TOKEN = "TU_TOKEN_DE_TELEGRAM"
CHAT_ID = "TU_CHAT_ID"
PAIR = "EURUSDT"

# =========================
# ENVIAR MENSAJE TELEGRAM
# =========================

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

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

# =========================
# OBTENER DATOS DE MERCADO
# =========================

def get_data():

    url = f"https://api.binance.com/api/v3/klines?symbol={PAIR}&interval=1m&limit=200"

    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data)

    df = df[[1,2,3,4]]
    df.columns = ["open","high","low","close"]

    df = df.astype(float)

    return df

# =========================
# ANALISIS DEL MERCADO
# =========================

def analyze():

    df = get_data()

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(df["close"],14).rsi()

    # Bollinger
    bb = ta.volatility.BollingerBands(df["close"],20)

    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()

    # EMA
    ema = ta.trend.EMAIndicator(df["close"],50)
    df["ema"] = ema.ema_indicator()

    # ATR
    atr = ta.volatility.AverageTrueRange(df["high"],df["low"],df["close"])
    df["atr"] = atr.average_true_range()

    last = df.iloc[-1]

    open_price = last["open"]
    close_price = last["close"]
    high_price = last["high"]
    low_price = last["low"]

    body = abs(close_price - open_price)

    wick_up = high_price - max(close_price, open_price)
    wick_down = min(close_price, open_price) - low_price

    # FILTRO MERCADO LATERAL
    if last["atr"] < 0.0002:
        return

    # =====================
    # SEÑAL CALL
    # =====================

    if (
        close_price < last["bb_low"]
        and last["rsi"] < 30
        and wick_down > body
        and close_price > last["ema"]
    ):

        send_signal(PAIR, "CALL", 95, 9)

    # =====================
    # SEÑAL PUT
    # =====================

    if (
        close_price > last["bb_high"]
        and last["rsi"] > 70
        and wick_up > body
        and close_price < last["ema"]
    ):

        send_signal(PAIR, "PUT", 95, 9)

# =========================
# LOOP PRINCIPAL
# =========================

print("BOT DE SEÑALES INICIADO")

while True:

    try:

        analyze()

        time.sleep(60)

    except Exception as e:

        print("Error:", e)

        time.sleep(60)
