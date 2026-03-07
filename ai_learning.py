import json
import os

ARCHIVO = "learning.json"


def cargar():

    if not os.path.exists(ARCHIVO):

        return {
            "wins": 0,
            "loss": 0
        }

    with open(ARCHIVO, "r") as f:
        return json.load(f)


def guardar(data):

    with open(ARCHIVO, "w") as f:
        json.dump(data, f)


def registrar(resultado):

    data = cargar()

    if resultado == "win":
        data["wins"] += 1

    if resultado == "loss":
        data["loss"] += 1

    guardar(data)


def winrate():

    data = cargar()

    total = data["wins"] + data["loss"]

    if total == 0:
        return 0

    return round((data["wins"] / total) * 100, 2)
