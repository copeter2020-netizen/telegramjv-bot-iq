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

if not TOKEN:
    raise ValueError("TOKEN no configurado")

bot = telebot.TeleBot(TOKEN)

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

AUTO = False
CHAT_ID = None
ULTIMA_OPERACION = 0

# =====================================
# CONECTAR IQ OPTION
# =====================================

def conectar_iq():

    if conector.conectar():
        print("✅ Conectado a IQ Option")
    else:
        print("❌ Error conexión IQ")

conectar_iq()

# =====================================
# OBTENER PARES DISPONIBLES
# =====================================

def obtener_pares():

    try:

        activos = conector.api.get_all_open_time()

        pares = []

        for tipo in activos:

            for par in activos[tipo]:

                if activos[tipo][par]["open"]:
                    pares.append(par)

        print("📊 Pares activos:", pares)

        return pares

    except Exception as e:

        print("Error obteniendo pares:", e)

        return []

# =====================================
# COMANDO COMENZAR
# =====================================

@bot.message_handler(commands=['comenzar'])
def comenzar(m):

    texto = (
        "🤖 BOT OTC ACTIVO\n\n"
        "/auto → activar señales\n"
        "/stop → detener señales\n\n"
        "El bot analizará todos los pares disponibles."
    )

    bot.reply_to(m, texto)

# =====================================
# AUTO
# =====================================

@bot.message_handler(commands=['auto'])
def auto(m):

    global AUTO, CHAT_ID

    AUTO = True
    CHAT_ID = m.chat.id

    bot.reply_to(m, "🚀 Señales automáticas activadas")

# =====================================
# STOP
# =====================================

@bot.message_handler(commands=['stop'])
def stop(m):

    global AUTO

    AUTO = False

    bot.reply_to(m, "⛔ Señales detenidas")

# =====================================
# ANALISIS AUTOMATICO
# =====================================

def auto_signals():

    global AUTO
    global ULTIMA_OPERACION

    while True:

        if AUTO and CHAT_ID:

            pares = obtener_pares()

            print("🔎 Analizando mercado...")

            for par in pares:

                if time.time() - ULTIMA_OPERACION < 300:
                    continue

                try:

                    resultado = analizar(conector, par)

                    if resultado:

                        mensaje = (
                            "🚨 SEÑAL DETECTADA\n\n"
                            f"Par: {par}\n"
                            f"Hora: {resultado['hora']}\n"
                            f"Dirección: {resultado['direccion']}\n"
                            f"Probabilidad: {resultado['probabilidad']}%\n"
                            f"Expiración: {resultado['expiracion']} minutos"
                        )

                        bot.send_message(CHAT_ID, mensaje)

                        ULTIMA_OPERACION = time.time()

                        print("Señal enviada:", par)

                except Exception as e:

                    print("Error analizando", par, e)

        time.sleep(10)

# =====================================
# INICIAR BOT
# =====================================

threading.Thread(target=auto_signals).start()

print("🚀 BOT CORRIENDO...")

bot.infinity_polling()
