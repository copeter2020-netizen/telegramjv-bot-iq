import telebot
import os
import time
import threading
from iq_connector import ConectorIQ
from strategy import analizar

# =====================================
# VARIABLES
# =====================================

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

bot = telebot.TeleBot(TOKEN)

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

AUTO = False
CHAT_ID = None
ULTIMA_OPERACION = 0


# =====================================
# PARES
# =====================================

PARES = {

"EURUSD": "EURUSD-OTC",
"GBPUSD": "GBPUSD-OTC",
"EURGBP": "EURGBP-OTC",
"AUDCAD": "AUDCAD-OTC"

}


# =====================================
# CONECTAR
# =====================================

def conectar():

    if conector.conectar():
        print("✅ Conectado a IQ Option")

    else:
        print("❌ Error conexión IQ")


conectar()


# =====================================
# ESPERAR CIERRE DE VELA
# =====================================

def esperar_cierre():

    while True:

        segundos = int(time.time()) % 60

        if segundos >= 59:
            break

        time.sleep(0.5)


# =====================================
# COMANDOS
# =====================================

@bot.message_handler(commands=['auto'])
def auto(m):

    global AUTO, CHAT_ID

    AUTO = True
    CHAT_ID = m.chat.id

    bot.reply_to(m, "🚀 Bot activado")


@bot.message_handler(commands=['stop'])
def stop(m):

    global AUTO

    AUTO = False

    bot.reply_to(m, "⛔ Bot detenido")


# =====================================
# ANALISIS AUTOMATICO
# =====================================

def auto_signals():

    global AUTO
    global ULTIMA_OPERACION

    while True:

        if AUTO and CHAT_ID:

            esperar_cierre()

            mejor_par = None
            mejor_resultado = None
            mejor_score = 0

            print("📊 Analizando cierre de vela...")

            for par in PARES.values():

                try:

                    resultado = analizar(conector, par)

                    if resultado:

                        score = resultado["score"]

                        if score > mejor_score:

                            mejor_score = score
                            mejor_par = par
                            mejor_resultado = resultado

                except Exception as e:

                    print("Error analizando", par, e)

            if mejor_resultado:

                if time.time() - ULTIMA_OPERACION > 120:

                    mensaje = (
                        "🚨 MEJOR SEÑAL\n\n"
                        f"Par: {mejor_par}\n"
                        f"Hora: {mejor_resultado['hora']}\n"
                        f"Dirección: {mejor_resultado['direccion']}\n"
                        f"Probabilidad: {mejor_resultado['probabilidad']}%\n"
                        f"Expiración: {mejor_resultado['expiracion']} minutos\n"
                        f"Score: {mejor_resultado['score']}"
                    )

                    bot.send_message(CHAT_ID, mensaje)

                    ULTIMA_OPERACION = time.time()

                    print("✅ Señal enviada:", mejor_par)

        time.sleep(1)


# =====================================
# INICIAR BOT
# =====================================

threading.Thread(target=auto_signals).start()

print("🚀 BOT CORRIENDO...")

bot.infinity_polling()
