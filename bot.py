import telebot
import os
import time
import threading
import datetime

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
"AUDUSD-OTC",
"EURJPY-OTC",
"GBPJPY-OTC",
"NZDUSD-OTC"
]

iq = ConectorIQ()
iq.conectar()


def enviar_senal(par, direccion, tiempo, conf):

    mensaje = f"""
📊 SEÑAL IQ OPTION

Par: {par}
Dirección: {direccion}

Entrada: siguiente vela
Expiración: {tiempo} minutos

Confirmaciones: {conf}
"""

    bot.send_message(CHAT_ID, mensaje)


def esperar_cierre_vela():

    ahora = datetime.datetime.utcnow()

    segundos = ahora.second

    esperar = 60 - segundos

    time.sleep(esperar)


def analizar_mercado():

    while True:

        esperar_cierre_vela()

        for par in pares:

            try:

                velas = iq.velas(par)

                if not velas:
                    print("Par no disponible:", par)
                    continue

                decision, tiempo, conf = analizar(velas)

                if decision:

                    enviar_senal(par, decision, tiempo, conf)

            except Exception as e:

                print("Error analizando:", par, e)


@bot.message_handler(commands=['start'])
def start(msg):

    bot.reply_to(msg, "🤖 Bot de señales iniciado")


hilo = threading.Thread(target=analizar_mercado)

hilo.daemon = True

hilo.start()


while True:

    try:

        bot.infinity_polling(timeout=60, long_polling_timeout=60)

    except Exception as e:

        print("Error polling:", e)

        time.sleep(10)
