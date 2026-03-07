import time
import numpy as np


# =====================================
# HORA
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

    highs = [v['max'] for v in velas[-30:]]
    lows = [v['min'] for v in velas[-30:]]

    return min(lows), max(highs)


# =====================================
# FUERZA DE VELA
# =====================================

def vela_fuerte(v):

    cuerpo = abs(v['close'] - v['open'])

    rango = v['max'] - v['min']

    if rango == 0:
        return False

    return cuerpo / rango > 0.6


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
# MERCADO LATERAL
# =====================================

def mercado_lateral(cierres):

    volatilidad = np.std(cierres[-20:])

    return volatilidad < 0.00005


# =====================================
# CONFIRMACION M5
# =====================================

def confirmacion_m5(conector, par):

    velas = conector.api.get_candles(par, 300, 50, time.time())

    cierres = [v['close'] for v in velas]

    ema50 = ema(cierres, 50)

    ema200 = ema(cierres, 200)

    if ema50[-1] > ema200[-1]:
        return "CALL"

    if ema50[-1] < ema200[-1]:
        return "PUT"

    return None


# =====================================
# EXPIRACION
# =====================================

def expiracion():

    return 5


# =====================================
# ESPERAR CIERRE VELA
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

    velas = conector.api.get_candles(par, 60, 120, time.time())

    cierres = [v['close'] for v in velas]

    if mercado_lateral(cierres):
        return None

    v1 = velas[-2]
    v2 = velas[-1]

    soporte, resistencia = soporte_resistencia(velas)

    ema50 = ema(cierres, 50)
    ema200 = ema(cierres, 200)

    tendencia_alcista = ema50[-1] > ema200[-1]
    tendencia_bajista = ema50[-1] < ema200[-1]

    patron = engulfing(v1, v2)

    confirmacion_mayor = confirmacion_m5(conector, par)

    confirmaciones = 0

    if vela_fuerte(v2):
        confirmaciones += 1

    if patron:
        confirmaciones += 1

    # ======================
    # CALL
    # ======================

    if v2['min'] <= soporte * 1.002 and tendencia_alcista:

        if pinbar_alcista(v2) or patron == "CALL":

            if confirmacion_mayor == "CALL":

                confirmaciones += 2

                if confirmaciones >= 3:

                    return {
                        "direccion": "CALL",
                        "probabilidad": 85,
                        "expiracion": expiracion(),
                        "hora": hora_entrada()
                    }


    # ======================
    # PUT
    # ======================

    if v2['max'] >= resistencia * 0.998 and tendencia_bajista:

        if pinbar_bajista(v2) or patron == "PUT":

            if confirmacion_mayor == "PUT":

                confirmaciones += 2

                if confirmaciones >= 3:

                    return {
                        "direccion": "PUT",
                        "probabilidad": 85,
                        "expiracion": expiracion(),
                        "hora": hora_entrada()
                    }

    return None 
