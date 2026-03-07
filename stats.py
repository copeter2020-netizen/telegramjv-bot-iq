import json
import os

ARCHIVO = "estadisticas.json"


def cargar():

    if not os.path.exists(ARCHIVO):

        return {
            "total": 0,
            "wins": 0,
            "loss": 0
        }

    with open(ARCHIVO, "r") as f:

        return json.load(f)


def guardar(data):

    with open(ARCHIVO, "w") as f:

        json.dump(data, f)


def registrar_resultado(win):

    data = cargar()

    data["total"] += 1

    if win:
        data["wins"] += 1
    else:
        data["loss"] += 1

    guardar(data)


def winrate():

    data = cargar()

    if data["total"] == 0:
        return 0

    return round((data["wins"] / data["total"]) * 100, 2)
