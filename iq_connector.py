from iqoptionapi.stable_api import IQ_Option
import os
import time

class ConectorIQ:

    def __init__(self):

        self.email = os.getenv("IQ_EMAIL")
        self.password = os.getenv("IQ_PASSWORD")

        self.API = IQ_Option(self.email, self.password)

    def conectar(self):

        while True:

            try:

                print("Conectando a IQ Option...")

                self.API.connect()

                if self.API.check_connect():
                    print("Conectado correctamente")
                    break

            except:
                print("Error conectando, reintentando...")

            time.sleep(5)

    def verificar_conexion(self):

        if not self.API.check_connect():

            print("Reconectando...")

            self.conectar()

    def velas(self, par):

        self.verificar_conexion()

        return self.API.get_candles(
            par,
            60,
            100,
            self.API.get_server_timestamp()
        )
