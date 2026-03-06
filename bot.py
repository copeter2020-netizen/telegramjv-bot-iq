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

# evita error 409
bot.delete_webhook()

print("Iniciando bot...")

# conectar a IQ Option
iq = ConectorIQ()
iq.conectar()

# PARES QUE ANALIZA EL BOT
pares = [
"EURUSD-OTC",
"GBPUSD-OTC",
"AUDCAD-OTC",
"AUDJPY-OTC"
]

print("Pares configurados:", pares)


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


def enviar_resultado(par, direccion, open_price, close_price):

    resultado = "LOSS"

    if direccion == "CALL":
        if close_price > open_price:
            resultado = "WIN"

    if direccion == "PUT":
        if close_price < open_price:
            resultado = "WIN"

    mensaje = f"""
📊 RESULTADO

Par: {par}
Dirección: {direccion}

Resultado: {resultado}
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

                if not decision:
                    continue

                ultima = velas[-1]

                open_price = ultima["open"]

                enviar_senal(par, decision, tiempo, conf)

                # esperar expiración
                time.sleep(tiempo * 60)

                velas_resultado = iq.velas(par)

                if not velas_resultado:
                    continue

                ultima_resultado = velas_resultado[-1]

                close_price = ultima_resultado["close"]

                enviar_resultado(par, decision, open_price, close_price)

            except Exception as e:

                print("Error analizando:", par, e)


@bot.message_handler(commands=['start'])
def start(msg):

    bot.reply_to(msg, "🤖 Bot de señales iniciado")


# hilo de análisis
hilo = threading.Thread(target=analizar_mercado)

hilo.daemon = True

hilo.start()


# polling estable
while True:

    try:

        bot.infinity_polling(timeout=60, long_polling_timeout=60)

    except Exception as e:

        print("Error polling:", e)

        time.sleep(10)
