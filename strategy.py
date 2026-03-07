import time
import numpy as np
from ai_learning import winrate


# =====================================
# HORA EXACTA DE ENTRADA
# =====================================

def hora_entrada():

    ahora = time.localtime()

    return f"{ahora.tm_hour:02d}:{ahora.tm_min:02d}:59"


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


# =====================================
# SOPORTE Y RESISTENCIA
# =====================================

def soporte_resistencia(velas):

    highs = [v['max'] for v in velas[-40:]]
    lows = [v['min'] for v in velas[-40:]]

    resistencia = max(highs)
    soporte = min(lows)

    return soporte, resistencia


# =====================================
# FILTRO MERCADO LATERAL
# =====================================

def mercado_lateral(cierres):

    return volatilidad(cierres) < 0.00004


# =====================================
# DETECTAR MANIPULACION OTC
# =====================================

def manipulacion_otc(velas):

    rangos = [v['max'] - v['min'] for v in velas[-10:]]

    media = np.mean(rangos)

    ultima = velas[-1]['max'] - velas[-1]['min']

    return ultima > media * 2.5


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
# VELA FUERTE
# =====================================

def vela_fuerte(v):

    cuerpo = abs(v['close'] - v['open'])

    rango = v['max'] - v['min']

    if rango == 0:
        return False

    return cuerpo / rango > 0.6


# =====================================
# CONFIRMACION TENDENCIA M5
# =====================================

def confirmacion_m5(conector, par):

    velas = conector.api.get_candles(par, 300, 300, time.time())

    cierres = [v['close'] for v in velas]

    ema50 = ema(cierres, 50)
    ema200 = ema(cierres, 200)

    if ema50[-1] > ema200[-1]:
        return "CALL"

    if ema50[-1] < ema200[-1]:
        return "PUT"

    return None


# =====================================
# ANALIZAR MERCADO
# =====================================

def analizar(conector, par):

    velas = conector.api.get_candles(par, 60, 300, time.time())

    cierres = [v['close'] for v in velas]

    if mercado_lateral(cierres):
        return None

    if manipulacion_otc(velas):
        return None

    soporte, resistencia = soporte_resistencia(velas)

    v1 = velas[-2]
    v2 = velas[-1]

    patron = engulfing(v1, v2)

    tendencia = confirmacion_m5(conector, par)

    score = 0


    # soporte
    if v2['min'] <= soporte * 1.002:

        score += 2

        if pinbar_alcista(v2) or patron == "CALL":
            score += 2


    # resistencia
    if v2['max'] >= resistencia * 0.998:

        score += 2

        if pinbar_bajista(v2) or patron == "PUT":
            score += 2


    if tendencia:
        score += 2

    if vela_fuerte(v2):
        score += 1

    if volatilidad(cierres) > 0.00008:
        score += 1


    # IA ADAPTATIVA

    wr = winrate()

    if wr < 60:
        minimo_score = 7
    elif wr < 75:
        minimo_score = 6
    else:
        minimo_score = 5


    if score < minimo_score:
        return None


    # EXPIRACION FIJA 1 MINUTO

    expiracion = 1


    if v2['min'] <= soporte * 1.002 and tendencia == "CALL":

        return {
            "direccion": "CALL",
            "probabilidad": 85 + score,
            "expiracion": expiracion,
            "hora": hora_entrada(),
            "score": score
        }


    if v2['max'] >= resistencia * 0.998 and tendencia == "PUT":

        return {
            "direccion": "PUT",
            "probabilidad": 85 + score,
            "expiracion": expiracion,
            "hora": hora_entrada(),
            "score": score
        }

    return None 
