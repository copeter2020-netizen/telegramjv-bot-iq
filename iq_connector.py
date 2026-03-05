from iqoptionapi.stable_api import IQ_Option
import os

class ConectorIQ:

    def __init__(self):
        self.email = os.getenv("IQ_EMAIL")
        self.password = os.getenv("IQ_PASSWORD")
        self.API = IQ_Option(self.email, self.password)

    def conectar(self):
        self.API.connect()

        if self.API.check_connect():
            print("Conectado a IQ Option")
        else:
            print("Error conectando")

        self.API.change_balance("PRACTICE")

    def velas(self, par, timeframe=60, cantidad=50):
        return self.API.get_candles(par, timeframe, cantidad, self.API.get_server_timestamp())
