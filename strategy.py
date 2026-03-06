import time
import numpy as np

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
# RSI
# =====================================

def calcular_rsi(cierres, periodo=14):

    cierres = np.array(cierres)

    delta = np.diff(cierres)

    subida = delta.clip(min=0)
    bajada = -delta.clip(max=0)

    media_subida = subida[-periodo:].mean()
    media_bajada = bajada[-periodo:].mean()

    if media_bajada == 0:
        return 100

    rs = media_subida / media_bajada

    rsi = 100 - (100 / (1 + rs))

    return rsi


# =====================================
# FILTRO MERCADO LATERAL
# =====================================

def mercado_lateral(cierres):

    volatilidad = np.std(cierres[-20:])

    if volatilidad < 0.00005:
        return True

    return False


# =====================================
# FILTRO MANIPULACION OTC
# =====================================

def manipulacion_otc(velas):

    rangos = [v['max'] - v['min'] for v in velas[-10:]]

    media = np.mean(rangos)

    ultima = velas[-1]['max'] - velas[-1]['min']

    if ultima > media * 3:
        return True

    return False


# =====================================
# CALCULAR PROBABILIDAD
# =====================================

def probabilidad(tendencia, rompimiento, rsi):

    score = 0

    if tendencia:
        score += 40

    if rompimiento:
        score += 40

    if rsi < 40 or rsi > 60:
        score += 20

    return score


# =====================================
# CALCULAR TIEMPO DE EXPIRACION
# =====================================

def calcular_expiracion(velas):

    rango = velas[-1]['max'] - velas[-1]['min']

    promedio = np.mean([v['max'] - v['min'] for v in velas[-10:]])

    if rango > promedio * 2:
        return "1 minuto"

    if rango > promedio:
        return "3 minutos"

    return "5 minutos"


# =====================================
# ANALIZAR MERCADO
# =====================================

def analizar(conector, par):

    velas = conector.api.get_candles(par, 60, 120, time.time())

    cierres = [v['close'] for v in velas]

    # FILTROS
    if manipulacion_otc(velas):
        return None

    if mercado_lateral(cierres):
        return None

    # RSI
    rsi = calcular_rsi(cierres)

    # TENDENCIA
    ema50 = ema(cierres, 50)
    ema100 = ema(cierres, 80)

    tendencia_alcista = ema50[-1] > ema100[-1]
    tendencia_bajista = ema50[-1] < ema100[-1]

    # SOPORTE Y RESISTENCIA
    maximos = [v['max'] for v in velas[-20:]]
    minimos = [v['min'] for v in velas[-20:]]

    resistencia = max(maximos[:-2])
    soporte = min(minimos[:-2])

    vela_actual = velas[-1]
    vela_anterior = velas[-2]

    expiracion = calcular_expiracion(velas)

    # =====================================
    # CALL
    # =====================================

    rompimiento = vela_anterior['close'] > resistencia
    retest = vela_actual['min'] <= resistencia

    vela_fuerte = vela_actual['close'] > vela_actual['open']

    if rompimiento and retest and tendencia_alcista and vela_fuerte and rsi < 60:

        prob = probabilidad(True, True, rsi)

        if prob >= 70:
            return f"CALL\nProbabilidad: {prob}%\nExpiración: {expiracion}"


    # =====================================
    # PUT
    # =====================================

    rompimiento = vela_anterior['close'] < soporte
    retest = vela_actual['max'] >= soporte

    vela_fuerte = vela_actual['close'] < vela_actual['open']

    if rompimiento and retest and tendencia_bajista and vela_fuerte and rsi > 40:

        prob = probabilidad(True, True, rsi)

        if prob >= 70:
            return f"PUT\nProbabilidad: {prob}%\nExpiración: {expiracion}"


    return None
