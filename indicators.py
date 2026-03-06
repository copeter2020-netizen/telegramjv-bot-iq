import pandas as pd

def calcular_rsi(df, periodo=14):

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(periodo).mean()
    avg_loss = loss.rolling(periodo).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calcular_ema(df, periodo=20):

    ema = df["close"].ewm(span=periodo).mean()

    return ema
