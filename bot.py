import time
import requests
import pandas as pd
from datetime import datetime
import ta
from iqoptionapi.stable_api import IQ_Option

# =============================
# CONFIGURACION
# =============================

IQ_EMAIL = "TU_EMAIL"
IQ_PASSWORD = "TU_PASSWORD"

TELEGRAM_TOKEN = "TU_TOKEN"
CHAT_ID = "TU_CHAT_ID"

# =============================
# CONEXION IQ OPTION
# =============================

def conectar_iq():

    while True:

        try:

            print("Conectando a IQ Option...")

            iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)

            iq.connect()

            time.sleep(5)

            if iq.check_connect():

                print("Conexion exitosa")

                iq.change_balance("PRACTICE")

                return iq

            else:

                print("Error de conexion, reintentando...")

        except Exception as e:

            print("Error:", e)

        time.sleep(10)


Iq = conectar_iq()

# =============================
# TELEGRAM
# =============================

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

    try:

        requests.post(url,data={"chat_id":CHAT_ID,"text":mensaje})

    except:

        print("Error enviando mensaje")


# =============================
# OBTENER PARES OTC
# =============================

def obtener_pares_otc():

    pares = []

    activos = Iq.get_all_open_time()

    for activo in activos["digital"]:

        if "OTC" in activo and activos["digital"][activo]["open"]:

            pares.append(activo)

    return pares


# =============================
# OBTENER VELAS
# =============================

def obtener_velas(par):

    velas = Iq.get_candles(par,60,200,time.time())

    df = pd.DataFrame(velas)

    df = df[["open","max","min","close"]]

    df.columns = ["open","high","low","close"]

    df = df.astype(float)

    return df


# =============================
# ANALISIS
# =============================

def analizar(par):

    df = obtener_velas(par)

    if len(df) < 50:
        return

    df["rsi"] = ta.momentum.RSIIndicator(df["close"],14).rsi()

    bb = ta.volatility.BollingerBands(df["close"],20)

    df["bb_high"] = bb.bollinger_hband()

    df["bb_low"] = bb.bollinger_lband()

    ultima = df.iloc[-1]

    cuerpo = abs(ultima["close"] - ultima["open"])

    mecha_arriba = ultima["high"] - max(ultima["close"],ultima["open"])

    mecha_abajo = min(ultima["close"],ultima["open"]) - ultima["low"]

    # CALL

    if ultima["close"] < ultima["bb_low"] and ultima["rsi"] < 30 and mecha_abajo > cuerpo:

        enviar_senal(par,"CALL")

    # PUT

    if ultima["close"] > ultima["bb_high"] and ultima["rsi"] > 70 and mecha_arriba > cuerpo:

        enviar_senal(par,"PUT")


# =============================
# LOOP PRINCIPAL
# =============================

print("BOT OTC INICIADO")

while True:

    try:

        pares = obtener_pares_otc()

        print("Pares OTC activos:", pares)

        for par in pares:

            analizar(par)

        time.sleep(60)

    except Exception as e:

        print("Error:",e)

        Iq = conectar_iq()

        time.sleep(10)
