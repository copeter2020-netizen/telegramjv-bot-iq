import time
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

    velas = conector.api.get_candles(par, 60, 50, time.time())

    cierres = [vela['close'] for vela in velas]

    rsi = calcular_rsi(cierres)

    ultima = velas[-1]
    anterior = velas[-2]

    tendencia_corta = np.mean(cierres[-5:])
    tendencia_larga = np.mean(cierres[-20:])

    # CALL
    if rsi < 30 and ultima['close'] > ultima['open'] and tendencia_corta > tendencia_larga:
        return "CALL"

    # PUT
    if rsi > 70 and ultima['close'] < ultima['open'] and tendencia_corta < tendencia_larga:
        return "PUT"

    return None 
