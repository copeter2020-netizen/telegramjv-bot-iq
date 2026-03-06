import telebot
import os
import time
import threading
from iq_connector import ConectorIQ
from strategy import analizar

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

bot = telebot.TeleBot(TOKEN)

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

AUTO = False
CHAT_ID = None
ULTIMA_SEÑAL = {}

PARES_OTC = {

"EURUSDOTC": "EURUSD-OTC",
"GBPUSDOTC": "GBPUSD-OTC",
"AUDUSDOTC": "AUDUSD-OTC",
"EURGBPOTC": "EURGBP-OTC",
"USDJPYOTC": "USDJPY-OTC",
"EURJPYOTC": "EURJPY-OTC",
"USDCADOTC": "USDCAD-OTC",
"NZDUSDOTC": "NZDUSD-OTC",
"GBPJPYOTC": "GBPJPY-OTC",
"AUDJPYOTC": "AUDJPY-OTC",
"CADJPYOTC": "CADJPY-OTC",
"EURCADOTC": "EURCAD-OTC",
"GBPCADOTC": "GBPCAD-OTC",
"NZDJPYOTC": "NZDJPY-OTC",
"EURCHFOTC": "EURCHF-OTC"
}

@bot.message_handler(commands=['comenzar'])
def comenzar(m):

    texto = (
        "🤖 BOT OTC ACTIVO\n\n"
        "Comandos:\n"
        "/auto → activar señales automáticas\n"
        "/stop → detener señales\n"
    )

    bot.reply_to(m, texto)


@bot.message_handler(commands=['auto'])
def auto(m):

    global AUTO, CHAT_ID

    AUTO = True
    CHAT_ID = m.chat.id

    bot.reply_to(m, "🚀 Señales automáticas activadas")


@bot.message_handler(commands=['stop'])
def stop(m):

    global AUTO

    AUTO = False

    bot.reply_to(m, "⛔ Señales detenidas")


@bot.message_handler(func=lambda m: True)
def manual(m):

    texto = m.text.upper()

    if texto in PARES_OTC:

        par = PARES_OTC[texto]

        resultado = analizar(conector, par)

        if resultado:

            mensaje = (
                "📊 SEÑAL OTC\n\n"
                f"Par: {par}\n"
                f"Hora: {resultado['hora']}\n"
                f"Dirección: {resultado['direccion']}\n"
                f"Probabilidad: {resultado['probabilidad']}%\n"
                f"Expiración: {resultado['expiracion']} minutos"
            )

            bot.reply_to(m, mensaje)

        else:

            bot.reply_to(m, "❌ No hay señal clara")


def auto_signals():

    global AUTO

    while True:

        if AUTO and CHAT_ID:

            print("🔎 Analizando mercado...")

            for par in PARES_OTC.values():

                try:

                    resultado = analizar(conector, par)

                    if resultado:

                        señal = resultado["direccion"]

                        if ULTIMA_SEÑAL.get(par) == señal:
                            continue

                        mensaje = (
                            "🚨 SEÑAL DETECTADA\n\n"
                            f"Par: {par}\n"
                            f"Hora: {resultado['hora']}\n"
                            f"Dirección: {resultado['direccion']}\n"
                            f"Probabilidad: {resultado['probabilidad']}%\n"
                            f"Expiración: {resultado['expiracion']} minutos"
                        )

                        bot.send_message(CHAT_ID, mensaje)

                        ULTIMA_SEÑAL[par] = señal

                        print("Señal enviada:", par)

                except Exception as e:

                    print("Error analizando", par, e)

        time.sleep(20)


threading.Thread(target=auto_signals).start()

print("🚀 BOT CORRIENDO...")

bot.infinity_polling() 
