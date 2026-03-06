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

    # =========================
    # CONFIRMACION CALL
    # =========================

    rompimiento = vela_anterior['close'] > resistencia
    retest = vela_actual['min'] <= resistencia

    vela_fuerte = vela_actual['close'] > vela_actual['open']

    if rompimiento and retest and tendencia_alcista and vela_fuerte and rsi < 60:

        prob = probabilidad(True, True, rsi)

        if prob >= 70:
            return f"CALL\nProbabilidad: {prob}%"

    # =========================
    # CONFIRMACION PUT
    # =========================

    rompimiento = vela_anterior['close'] < soporte
    retest = vela_actual['max'] >= soporte

    vela_fuerte = vela_actual['close'] < vela_actual['open']

    if rompimiento and retest and tendencia_bajista and vela_fuerte and rsi > 40:

        prob = probabilidad(True, True, rsi)

        if prob >= 70:
            return f"PUT\nProbabilidad: {prob}%"

    return None
