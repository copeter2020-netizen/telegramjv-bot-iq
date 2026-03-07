import time
import numpy as np
from ai_learning import winrate


def hora():

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
# VOLATILIDAD
# =====================================

def volatilidad(cierres):

    return np.std(cierres[-20:])


def mercado_lateral(cierres):

    return volatilidad(cierres) < 0.00004


# =====================================
# MANIPULACION OTC
# =====================================

def manipulacion_otc(velas):

    rangos = [v['max'] - v['min'] for v in velas[-10:]]

    media = np.mean(rangos)

    ultima = velas[-1]['max'] - velas[-1]['min']

    return ultima > media * 3


# =====================================
# LIQUIDITY SWEEP
# =====================================

def liquidez(velas):

    highs = [v['max'] for v in velas[-20:]]
    lows = [v['min'] for v in velas[-20:]]

    maximo = max(highs)
    minimo = min(lows)

    ultima = velas[-1]

    if ultima['max'] > maximo:
        return "PUT"

    if ultima['min'] < minimo:
        return "CALL"

    return None


# =====================================
# ORDER BLOCK
# =====================================

def order_block(velas):

    for v in velas[-10:]:

        cuerpo = abs(v['close'] - v['open'])
        rango = v['max'] - v['min']

        if rango == 0:
            continue

        fuerza = cuerpo / rango

        if fuerza > 0.7:

            if v['close'] > v['open']:
                return "CALL"

            if v['close'] < v['open']:
                return "PUT"

    return None


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
# VELA FUERTE
# =====================================

def vela_fuerte(v):

    cuerpo = abs(v['close'] - v['open'])

    rango = v['max'] - v['min']

    if rango == 0:
        return False

    return cuerpo / rango > 0.6


# =====================================
# CONFIRMACION M5
# =====================================

def confirmacion_m5(conector, par):

    velas = conector.api.get_candles(par, 300, 200, time.time())

    cierres = [v['close'] for v in velas]

    ema50 = ema(cierres, 50)
    ema200 = ema(cierres, 200)

    if ema50[-1] > ema200[-1]:
        return "CALL"

    if ema50[-1] < ema200[-1]:
        return "PUT"

    return None


# =====================================
# ANALIZAR
# =====================================

def analizar(conector, par):

    velas = conector.api.get_candles(par, 60, 300, time.time())

    cierres = [v['close'] for v in velas]

    if mercado_lateral(cierres):
        return None

    if manipulacion_otc(velas):
        return None

    v1 = velas[-2]
    v2 = velas[-1]

    patron = engulfing(v1, v2)

    tendencia = confirmacion_m5(conector, par)

    sweep = liquidez(velas)

    bloque = order_block(velas)

    score = 0

    if sweep:
        score += 2

    if bloque:
        score += 2

    if patron:
        score += 2

    if tendencia:
        score += 2

    if vela_fuerte(v2):
        score += 1

    if volatilidad(cierres) > 0.00008:
        score += 1


    # =====================================
    # IA ADAPTATIVA
    # =====================================

    wr = winrate()

    if wr < 60:
        minimo_score = 7
    elif wr < 75:
        minimo_score = 6
    else:
        minimo_score = 5


    if score < minimo_score:
        return None


    if (patron == "CALL" or sweep == "CALL" or bloque == "CALL") and tendencia == "CALL":

        return {
            "direccion": "CALL",
            "probabilidad": 98,
            "expiracion": 2,
            "hora": hora(),
            "score": score
        }


    if (patron == "PUT" or sweep == "PUT" or bloque == "PUT") and tendencia == "PUT":

        return {
            "direccion": "PUT",
            "probabilidad": 98,
            "expiracion": 2,
            "hora": hora(),
            "score": score
        }

    return None 
