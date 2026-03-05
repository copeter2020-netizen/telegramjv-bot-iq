import pandas as pd
from indicators import calcular_rsi, calcular_ema

def analizar(candles):

    df = pd.DataFrame(candles)

    df["ema"] = calcular_ema(df)
    df["rsi"] = calcular_rsi(df)

    confirmaciones_call = 0
    confirmaciones_put = 0

    ultima = df.iloc[-1]

    # tendencia EMA
    if ultima["close"] > ultima["ema"]:
        confirmaciones_call += 1

    if ultima["close"] < ultima["ema"]:
        confirmaciones_put += 1

    # RSI
    if ultima["rsi"] < 30:
        confirmaciones_call += 1

    if ultima["rsi"] > 70:
        confirmaciones_put += 1

    # soporte
    soporte = df["low"].tail(10).min()

    if abs(ultima["close"] - soporte) < 0.0003:
        confirmaciones_call += 1

    # resistencia
    resistencia = df["high"].tail(10).max()

    if abs(ultima["close"] - resistencia) < 0.0003:
        confirmaciones_put += 1

    # cambio de tendencia
    if df["close"].iloc[-3] < df["close"].iloc[-2] < df["close"].iloc[-1]:
        confirmaciones_call += 1

    if df["close"].iloc[-3] > df["close"].iloc[-2] > df["close"].iloc[-1]:
        confirmaciones_put += 1

    # decisión final

    if confirmaciones_call >= 3:
        return "CALL", 4, confirmaciones_call

    if confirmaciones_put >= 3:
        return "PUT", 4, confirmaciones_put

    return None, None, 0
