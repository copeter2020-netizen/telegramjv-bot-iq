import telebot
import os
import time
from iq_connector import ConectorIQ
from strategy import analizar

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

pares = [
    "EURUSD-OTC",
    "GBPUSD-OTC",
    "AUDCAD-OTC"
]

iq = ConectorIQ()
iq.conectar()

def enviar_senal(par, direccion):

    mensaje = f"""
📊 SEÑAL DETECTADA

Par: {par}
Dirección: {direccion}

Entrada: siguiente vela
Expiración: 3-5 minutos
"""

    bot.send_message(CHAT_ID, mensaje)

def analizar_mercado():

    while True:

        for par in pares:

            velas = iq.velas(par)

            decision = analizar(velas)

            if decision:

                enviar_senal(par, decision)

        time.sleep(60)

@bot.message_handler(commands=['start'])
def start(msg):

    bot.reply_to(msg, "Bot de señales iniciado")

import threading

hilo = threading.Thread(target=analizar_mercado)
hilo.start()

bot.infinity_polling()
