import telebot
import os
import time
import threading
from iq_connector import ConectorIQ
from strategy import analizar

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

pares = [
    "EURUSD-OTC",
    "GBPUSD-OTC",
    "AUDCAD-OTC",
    "USDJPY-OTC",
    "EURGBP-OTC",
    "USDCAD-OTC",
    "AUDUSD-OTC",
    "EURJPY-OTC",
    "GBPJPY-OTC"
]

iq = ConectorIQ()
iq.conectar()


def enviar_senal(par, direccion, tiempo):

    mensaje = f"""
📊 SEÑAL IQ OPTION

Par: {par}
Dirección: {direccion}

Entrada: siguiente vela
Expiración: {tiempo} minutos
"""

    bot.send_message(CHAT_ID, mensaje)


def analizar_mercado():

    while True:

        try:

            for par in pares:

                velas = iq.velas(par)

                decision, tiempo, conf = analizar(velas)

                if decision:

                    enviar_senal(par, decision, tiempo)

        except Exception as e:

            print("Error analizando:", e)

        time.sleep(60)


@bot.message_handler(commands=['start'])
def start(msg):

    bot.reply_to(msg, "🤖 Bot de señales iniciado")


# hilo para análisis del mercado
hilo = threading.Thread(target=analizar_mercado)
hilo.daemon = True
hilo.start()


# polling seguro (anti congelamiento)
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Error polling:", e)
        time.sleep(10)
