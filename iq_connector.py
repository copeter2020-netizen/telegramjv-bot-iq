from iqoptionapi.stable_api import IQ_Option
import os
import time


class ConectorIQ:

    def __init__(self):

        email = os.getenv("IQ_EMAIL")
        password = os.getenv("IQ_PASSWORD")

        self.API = IQ_Option(email, password)

    def conectar(self):

        while True:

            try:

                print("Conectando a IQ Option...")

                self.API.connect()

                if self.API.check_connect():

                    print("Conectado correctamente")

                    break

            except Exception as e:

                print("Error conectando:", e)

            time.sleep(5)

    def velas(self, par):

        try:

            velas = self.API.get_candles(
                par,
                60,
                100,
                self.API.get_server_timestamp()
            )

            return velas

        except Exception as e:

            print("Error obteniendo velas:", e)
            return None


    # NUEVA FUNCIÓN
    def obtener_pares_abiertos(self):

        activos = self.API.get_all_open_time()

        pares_otc = []

        for par in activos["binary"]:

            if "OTC" in par:

                if activos["binary"][par]["open"]:

                    pares_otc.append(par)

        return pares_otc 
