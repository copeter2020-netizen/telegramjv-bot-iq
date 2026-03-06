from iqoptionapi.stable_api import IQ_Option
import time

class ConectorIQ:

    def __init__(self, email, password):

        self.email = email
        self.password = password
        self.api = None

    def conectar(self):

        try:

            self.api = IQ_Option(self.email, self.password)

            self.api.connect()

            if self.api.check_connect():

                print("✅ Conectado a IQ Option")
                return True

            else:

                print("❌ No se pudo conectar a IQ Option")
                return False

        except Exception as e:

            print("Error conectando:", e)
            return False 
