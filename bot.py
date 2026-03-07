import time
import requests
import pandas as pd
from datetime import datetime
import ta
from iqoptionapi.stable_api import IQ_Option

IQ_EMAIL = "TU_EMAIL"
IQ_PASSWORD = "TU_PASSWORD"

TELEGRAM_TOKEN = "TU_TOKEN"
CHAT_ID = "TU_CHAT_ID"

def conectar():

    while True:

        print("Conectando a IQ Option...")

        iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)

        iq.connect()

        if iq.check_connect():

            print("Conectado correctamente")

            iq.change_balance("PRACTICE")

            return iq

        else:

            print("Error de conexión, reintentando...")

            time.sleep(10)

Iq = conectar()

def enviar_senal(par, direccion):

    hora = datetime.utcnow().strftime("%H:%M:59")

    mensaje = f"""
🚨 MEJOR SEÑAL

Par: {par}
Hora: {hora}
Dirección: {direccion}
Expiración: 1 minuto
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(url,data={"chat_id":CHAT_ID,"text":mensaje})


def pares_otc():

    activos = Iq.get_all_open_time()

    pares = []

    for activo in activos["digital"]:

        if "OTC" in activo and activos["digital"][activo]["open"]:

            pares.append(activo)

    return pares


def velas(par):

    candles = Iq.get_candles(par,60,200,time.time())

    df = pd.DataFrame(candles)

    df = df[["open","max","min","close"]]

    df.columns = ["open","high","low","close"]

    df = df.astype(float)

    return df


def analizar(par):

    df = velas(par)

    if len(df) < 50:
        return

    df["rsi"] = ta.momentum.RSIIndicator(df["close"],14).rsi()

    bb = ta.volatility.BollingerBands(df["close"],20)

    df["bb_high"] = bb.bollinger_hband()

    df["bb_low"] = bb.bollinger_lband()

    ultima = df.iloc[-1]

    cuerpo = abs(ultima["close"] - ultima["open"])

    wick_up = ultima["high"] - max(ultima["close"],ultima["open"])

    wick_down = min(ultima["close"],ultima["open"]) - ultima["low"]

    if ultima["close"] < ultima["bb_low"] and ultima["rsi"] < 30 and wick_down > cuerpo:

        enviar_senal(par,"CALL")

    if ultima["close"] > ultima["bb_high"] and ultima["rsi"] > 70 and wick_up > cuerpo:

        enviar_senal(par,"PUT")


print("BOT OTC INICIADO")

while True:

    try:

        lista = pares_otc()

        print("Pares activos:", lista)

        for par in lista:

            analizar(par)

        time.sleep(60)

    except Exception as e:

        print("Error:", e)

        Iq = conectar()
