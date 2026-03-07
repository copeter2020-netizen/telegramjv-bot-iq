from flask import Flask
from stats import cargar, winrate

app = Flask(__name__)


@app.route("/")
def panel():

    data = cargar()

    html = f"""
    <h1>📊 Estadísticas del Bot</h1>

    <p>Total señales: {data['total']}</p>
    <p>Ganadas: {data['wins']}</p>
    <p>Perdidas: {data['loss']}</p>
    <p>Winrate: {winrate()}%</p>
    """

    return html


app.run(host="0.0.0.0", port=3000)
