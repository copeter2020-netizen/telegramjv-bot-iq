import time
import numpy as np


def hora_entrada():

    ahora = time.localtime()

    return f"{ahora.tm_hour:02d}:{ahora.tm_min:02d}"


def ema(data, period):

    data = np.array(data)

    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()

    a = np.convolve(data, weights, mode='full')[:len(data)]

    a[:period] = a[period]

    return a


def mercado_lateral(cierres):

    volatilidad = np.std(cierres[-20:])

    return volatilidad < 0.00005


def engulfing(v1, v2):

    if v1['close'] < v1['open'] and v2['close'] > v2['open']:

        if v2['close'] > v1['open'] and v2['open'] < v1['close']:
            return "CALL"

    if v1['close'] > v1['open'] and v2['close'] < v2['open']:

        if v2['open'] > v1['close'] and v2['close'] < v1['open']:
            return "PUT"

    return None


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

    v1 = velas[-2]
    v2 = velas[-1]

    patron = engulfing(v1, v2)

    confirmacion = confirmacion_m5(conector, par)

    if patron == "CALL" and confirmacion == "CALL":

        return {
            "direccion": "CALL",
            "probabilidad": 86,
            "expiracion": 2,
            "hora": hora_entrada()
        }

    if patron == "PUT" and confirmacion == "PUT":

        return {
            "direccion": "PUT",
            "probabilidad": 86,
            "expiracion": 2,
            "hora": hora_entrada()
        }

    return None 
