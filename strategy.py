import time
import numpy as np


# =====================================
# HORA DE ENTRADA
# =====================================

def hora_entrada():

    ahora = time.localtime()

    return f"{ahora.tm_hour:02d}:{ahora.tm_min:02d}"


# =====================================
# EMA
# =====================================

def ema(data, period):

    data = np.array(data)

    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()

    a = np.convolve(data, weights, mode='full')[:len(data)]

    a[:period] = a[period]

    return a


# =====================================
# SOPORTE Y RESISTENCIA
# =====================================

def soporte_resistencia(velas):

    highs = [v['max'] for v in velas[-40:]]
    lows = [v['min'] for v in velas[-40:]]

    return min(lows), max(highs)


# =====================================
# ESTRUCTURA DEL MERCADO
# =====================================

def estructura(velas):

    highs = [v['max'] for v in velas[-6:]]
    lows = [v['min'] for v in velas[-6:]]

    if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        return "alcista"

    if highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        return "bajista"

    return "lateral"


# =====================================
# FUERZA DE VELA
# =====================================

def fuerza_vela(vela):

    cuerpo = abs(vela['close'] - vela['open'])
    rango = vela['max'] - vela['min']

    if rango == 0:
        return False

    return cuerpo / rango > 0.6


# =====================================
# PINBAR
# =====================================

def pinbar_alcista(v):

    cuerpo = abs(v['close'] - v['open'])

    mecha = min(v['open'], v['close']) - v['min']

    return mecha > cuerpo * 2


def pinbar_bajista(v):

    cuerpo = abs(v['close'] - v['open'])

    mecha = v['max'] - max(v['open'], v['close'])

    return mecha > cuerpo * 2


# =====================================
# ENGULFING
# =====================================

def engulfing(v1, v2):

    if v1['close'] < v1['open'] and v2['close'] > v2['open']:

        if v2['close'] > v1['open'] and v2['open'] < v1['close']:
            return "CALL"

    if v1['close'] > v1['open'] and v2['close'] < v2['open']:

        if v2['open'] > v1['close'] and v2['close'] < v1['open']:
            return "PUT"

    return None


# =====================================
# CONFIRMACION MARCO MAYOR (M30)
# =====================================

def confirmacion_m30(conector, par):

    velas = conector.api.get_candles(par, 1800, 50, time.time())

    cierres = [v['close'] for v in velas]

    ema20 = ema(cierres, 20)

    tendencia_alcista = cierres[-1] > ema20[-1]
    tendencia_bajista = cierres[-1] < ema20[-1]

    v1 = velas[-2]
    v2 = velas[-1]

    patron = engulfing(v1, v2)

    if tendencia_alcista or patron == "CALL":
        return "CALL"

    if tendencia_bajista or patron == "PUT":
        return "PUT"

    return None


# =====================================
# EXPIRACION
# =====================================

def expiracion(velas):

    rango = velas[-1]['max'] - velas[-1]['min']

    promedio = np.mean([v['max'] - v['min'] for v in velas[-10:]])

    if rango > promedio * 2:
        return 1

    if rango > promedio * 1.5:
        return 2

    if rango > promedio:
        return 3

    return 4


# =====================================
# ESPERAR CIERRE DE VELA
# =====================================

def esperar_cierre():

    while True:

        if int(time.time()) % 60 >= 59:
            break

        time.sleep(0.5)


# =====================================
# ANALIZAR
# =====================================

def analizar(conector, par):

    esperar_cierre()

    velas = conector.api.get_candles(par, 60, 100, time.time())

    v1 = velas[-2]
    v2 = velas[-1]

    soporte, resistencia = soporte_resistencia(velas)

    estr = estructura(velas)

    exp = expiracion(velas)

    confirmaciones = 0

    patron = engulfing(v1, v2)

    if patron:
        confirmaciones += 1

    if fuerza_vela(v2):
        confirmaciones += 1

    if estr != "lateral":
        confirmaciones += 1

    prob = confirmaciones * 20


    # ======================
    # CALL
    # ======================

    if v2['min'] <= soporte * 1.002 and estr == "alcista":

        if pinbar_alcista(v2) or patron == "CALL":

            direccion_m30 = confirmacion_m30(conector, par)

            if direccion_m30 == "CALL":

                if prob >= 60:

                    return {
                        "direccion": "CALL",
                        "probabilidad": prob,
                        "expiracion": exp,
                        "hora": hora_entrada()
                    }


    # ======================
    # PUT
    # ======================

    if v2['max'] >= resistencia * 0.998 and estr == "bajista":

        if pinbar_bajista(v2) or patron == "PUT":

            direccion_m30 = confirmacion_m30(conector, par)

            if direccion_m30 == "PUT":

                if prob >= 60:

                    return {
                        "direccion": "PUT",
                        "probabilidad": prob,
                        "expiracion": exp,
                        "hora": hora_entrada()
                    }

    return None
