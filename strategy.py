import time
import numpy as np


# =====================================
# DETECTAR SOPORTE Y RESISTENCIA
# =====================================

def soporte_resistencia(velas):

    maximos = [v['max'] for v in velas[-30:]]
    minimos = [v['min'] for v in velas[-30:]]

    resistencia = max(maximos)
    soporte = min(minimos)

    return soporte, resistencia


# =====================================
# FUERZA DE VELA
# =====================================

def vela_fuerte(vela):

    cuerpo = abs(vela['close'] - vela['open'])
    rango = vela['max'] - vela['min']

    if rango == 0:
        return False

    fuerza = cuerpo / rango

    return fuerza > 0.6


# =====================================
# RECHAZO DE PRECIO
# =====================================

def rechazo_soporte(vela):

    cuerpo = abs(vela['close'] - vela['open'])

    mecha_inferior = min(vela['open'], vela['close']) - vela['min']

    return mecha_inferior > cuerpo


def rechazo_resistencia(vela):

    cuerpo = abs(vela['close'] - vela['open'])

    mecha_superior = vela['max'] - max(vela['open'], vela['close'])

    return mecha_superior > cuerpo


# =====================================
# CALCULAR PROBABILIDAD
# =====================================

def calcular_probabilidad(fuerza, rechazo, estructura):

    score = 0

    if fuerza:
        score += 40

    if rechazo:
        score += 30

    if estructura:
        score += 30

    return score


# =====================================
# ESTRUCTURA DEL MERCADO
# =====================================

def estructura_mercado(velas):

    highs = [v['max'] for v in velas[-10:]]
    lows = [v['min'] for v in velas[-10:]]

    if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        return "alcista"

    if highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        return "bajista"

    return "lateral"


# =====================================
# CALCULAR EXPIRACION
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

    velas = conector.api.get_candles(par, 60, 60, time.time())

    soporte, resistencia = soporte_resistencia(velas)

    vela_actual = velas[-1]

    estructura = estructura_mercado(velas)

    expiracion = calcular_expiracion(velas)

    fuerza = vela_fuerte(vela_actual)

    # ===============================
    # CALL
    # ===============================

    cerca_soporte = vela_actual['min'] <= soporte * 1.002

    rechazo = rechazo_soporte(vela_actual)

    if cerca_soporte and rechazo and estructura == "alcista":

        prob = calcular_probabilidad(fuerza, rechazo, True)

        if prob >= 60:

            return {
                "direccion": "CALL",
                "probabilidad": prob,
                "expiracion": expiracion
            }

    # ===============================
    # PUT
    # ===============================

    cerca_resistencia = vela_actual['max'] >= resistencia * 0.998

    rechazo = rechazo_resistencia(vela_actual)

    if cerca_resistencia and rechazo and estructura == "bajista":

        prob = calcular_probabilidad(fuerza, rechazo, True)

        if prob >= 60:

            return {
                "direccion": "PUT",
                "probabilidad": prob,
                "expiracion": expiracion
            }

    return None
