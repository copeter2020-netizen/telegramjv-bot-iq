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

# eliminar webhook para evitar conflicto 409
bot.delete_webhook()

print("Iniciando bot...")

# conectar a IQ Option
iq = ConectorIQ()
iq.conectar()

# obtener pares OTC activos
pares = iq.obtener_pares_abiertos()

print("Pares OTC activos:", pares)


def enviar_senal(par, direccion, tiempo, confirmaciones):

    mensaje = f"""
📊 SEÑAL IQ OPTION

Par: {par}
Dirección: {direccion}

Entrada: siguiente vela
Expiración: {tiempo} minutos

Confirmaciones: {confirmaciones}
"""

    bot.send_message(CHAT_ID, mensaje)


def esperar_cierre_vela():

    ahora = datetime.datetime.now(datetime.UTC)

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


# hilo que analiza el mercado
hilo = threading.Thread(target=analizar_mercado)

hilo.daemon = True

hilo.start()


# polling seguro para telegram
while True:

    try:

        bot.infinity_polling(timeout=60, long_polling_timeout=60)

    except Exception as e:

        print("Error polling:", e)

        time.sleep(10) 
