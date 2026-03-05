import pandas as pd

def analizar(candles):

    df = pd.DataFrame(candles)

    df["color"] = df.apply(
        lambda x: "verde" if x["close"] > x["open"] else "rojo",
        axis=1
    )

    ultimas = df["color"].tail(3).tolist()

    if ultimas.count("verde") >= 2:
        return "CALL"

    if ultimas.count("rojo") >= 2:
        return "PUT"

    return None
