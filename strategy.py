import time
import numpy as np


def hora():

    ahora = time.localtime()

    return f"{ahora.tm_hour:02d}:{ahora.tm_min:02d}"


def ema(data, period):

    data = np.array(data)

    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()

    a = np.convolve(data, weights, mode='full')[:len(data)]

    a[:period] = a[period]

    return a


def volatilidad(cierres):

    return np.std(cierres[-20:])


def mercado_lateral(cierres):

    return volatilidad(cierres) < 0.00004


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


def vela_fuerte(v):

    cuerpo = abs(v['close'] - v['open'])

    rango = v['max'] - v['min']

    if rango == 0:
        return False

    return cuerpo / rango > 0.6


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

    score = 0

    if sweep:
        score += 2

    if patron:
        score += 2

    if tendencia:
        score += 2

    if vela_fuerte(v2):
        score += 1

    if volatilidad(cierres) > 0.00008:
        score += 1

    if score < 5:
        return None


    if (patron == "CALL" or sweep == "CALL") and tendencia == "CALL":

        return {
            "direccion": "CALL",
            "probabilidad": 97,
            "expiracion": 2,
            "hora": hora(),
            "score": score
        }

    if (patron == "PUT" or sweep == "PUT") and tendencia == "PUT":

        return {
            "direccion": "PUT",
            "probabilidad": 97,
            "expiracion": 2,
            "hora": hora(),
            "score": score
        }

    return None 
