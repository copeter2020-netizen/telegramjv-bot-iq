import telebot
import time
import os
from iqoptionapi.stable_api import IQ_Option

TOKEN = os.getenv("TOKEN")
EMAIL = os.getenv("IQ_EMAIL")
PASSWORD = os.getenv("IQ_PASSWORD")

bot = telebot.TeleBot(TOKEN)

iq = IQ_Option(EMAIL, PASSWORD)
iq.connect()

par = "EURUSD-OTC"
timeframe = 60

def analizar():
    
    velas = iq.get_candles(par, timeframe, 10, time.time())

    verde = 0
    roja = 0

    for vela in velas:

        if vela["open"] < vela["close"]:
            verde += 1
        else:
            roja += 1

    if verde > roja:
        return "CALL"
    else:
        return "PUT"

def enviar_senal():

    while True:

        direccion = analizar()

        mensaje = f"""
📊 SEÑAL DETECTADA

Par: {par}
Dirección: {direccion}

⏱ Expiración
3m - 4m - 5m
"""

        bot.send_message(TU_CHAT_ID, mensaje)

        time.sleep(60)

@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(message.chat.id,"Bot conectado")

if __name__ == "__main__":

    enviar_senal()
