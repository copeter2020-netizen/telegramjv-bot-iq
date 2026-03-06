import numpy as np

def calcular_rsi(cierres, periodo=14):

    cierres = np.array(cierres)

    delta = np.diff(cierres)

    subida = delta.clip(min=0)
    bajada = -1 * delta.clip(max=0)

    media_subida = subida[-periodo:].mean()
    media_bajada = bajada[-periodo:].mean()

    if media_bajada == 0:
        return 100

    rs = media_subida / media_bajada

    rsi = 100 - (100 / (1 + rs))

    return rsi


def analizar(conector, par):

    velas = conector.api.get_candles(par, 60, 30, time.time())

    cierres = [v['close'] for v in velas]

    rsi = calcular_rsi(cierres)

    ultima = velas[-1]
    anterior = velas[-2]

    # tendencia
    tendencia = np.mean(cierres[-5:]) - np.mean(cierres[-15:-5])

    # señal CALL
    if rsi < 30 and ultima['close'] > ultima['open'] and tendencia > 0:
        return "📈 CALL"

    # señal PUT
    if rsi > 70 and ultima['close'] < ultima['open'] and tendencia < 0:
        return "📉 PUT"

    return None 
