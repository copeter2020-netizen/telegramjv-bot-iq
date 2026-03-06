import pandas as pd
import ta

def analizar(velas):

    if not velas or len(velas) < 100:
        return "⚠ Datos insuficientes para analizar"

    df = pd.DataFrame(velas)

    if "close" not in df.columns:
        return "⚠ Datos inválidos"

    # =========================
    # INDICADORES
    # =========================

    df["ema20"] = ta.trend.ema_indicator(df["close"], window=20)
    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    df = df.dropna()

    if df.empty:
        return "⚠ Esperando confirmación del mercado"

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # =========================
    # FILTRO DE MERCADO LATERAL
    # =========================

    if abs(last["ema20"] - last["ema50"]) < 0.00005:
        return "🟡 Mercado lateral — No operar"

    # =========================
    # SEÑAL CALL
    # =========================

    if (
        last["ema20"] > last["ema50"]
        and last["rsi"] > 55
        and last["macd"] > last["macd_signal"]
        and prev["macd"] <= prev["macd_signal"]
    ):
        return (
            "🟢 COMPRA (CALL)\n"
            "⏳ Expira en 5 minutos\n"
            "📈 Tendencia alcista confirmada\n"
            "📊 EMA20 > EMA50 + RSI fuerte + Cruce MACD"
        )

    # =========================
    # SEÑAL PUT
    # =========================

    if (
        last["ema20"] < last["ema50"]
        and last["rsi"] < 45
        and last["macd"] < last["macd_signal"]
        and prev["macd"] >= prev["macd_signal"]
    ):
        return (
            "🔴 VENTA (PUT)\n"
            "⏳ Expira en 5 minutos\n"
            "📉 Tendencia bajista confirmada\n"
            "📊 EMA20 < EMA50 + RSI débil + Cruce MACD"
        )

    return "🟡 Esperando mejor confirmación del mercado"
