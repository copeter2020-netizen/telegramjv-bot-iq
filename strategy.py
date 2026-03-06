import time
import numpy as np

# ==========================
# EMA
# ==========================

def ema(data, period):
    data = np.array(data)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()

    a = np.convolve(data, weights, mode='full')[:len(data)]
    a[:period] = a[period]

    return a


# ==========================
# RSI
# ==========================

def rsi(cierres, periodo=14):

    cierres = np.array(cierres)
    delta = np.diff(cierres)

    subida = delta.clip(min=0)
    bajada = -delta.clip(max=0)

    avg_up = subida[-periodo:].mean()
    avg_down = bajada[-periodo:].mean()

    if avg_down == 0:
        return 100

    rs = avg_up / avg_down

    return 100 - (100 / (1 + rs))


# ==========================
# DETECTAR ROMPIMIENTO
# ==========================

def breakout(velas):

    maximos = [v['max'] for v in velas[-20:]]
    minimos = [v['min'] for v in velas[-20:]]

    resistencia = max(maximos[:-1])
    soporte = min(minimos[:-1])

    ultima = velas[-1]

    if ultima['close'] > resistencia:
        return "CALL"

    if ultima['close'] < soporte:
        return "PUT"

    return None


# ==========================
# FILTRO MANIPULACION OTC
# ==========================

def manipulacion_otc(velas):

    rangos = [v['max'] - v['min'] for v in velas[-10:]]

    media = np.mean(rangos)

    ultima = velas[-1]['max'] - velas[-1]['min']

    # vela demasiado grande = posible manipulación
    if ultima > media * 3:
        return True

    return False


# ==========================
# SCORE (IA SIMPLE)
# ==========================

def score(prob):

    if prob >= 80:
        return "FUERTE"

    if prob >= 60:
        return "MEDIA"

    return "DEBIL"


# ==========================
# ANALIZAR
# ==========================

def analizar(conector, par):

    velas = conector.api.get_candles(par, 60, 120, time.time())

    cierres = [v['close'] for v in velas]

    ema50 = ema(cierres, 50)
    ema100 = ema(cierres, 80)

    tendencia_up = ema50[-1] > ema100[-1]
    tendencia_down = ema50[-1] < ema100[-1]

    r = rsi(cierres)

    if manipulacion_otc(velas):
        return None

    romp = breakout(velas)

    prob = 0

    if romp:
        prob += 40

    if tendencia_up or tendencia_down:
        prob += 30

    if r < 40 or r > 60:
        prob += 30

    calidad = score(prob)

    if romp == "CALL" and tendencia_up and prob >= 60:

        return f"CALL\nProbabilidad: {prob}%\nSeñal: {calidad}"

    if romp == "PUT" and tendencia_down and prob >= 60:

        return f"PUT\nProbabilidad: {prob}%\nSeñal: {calidad}"

    return None 
