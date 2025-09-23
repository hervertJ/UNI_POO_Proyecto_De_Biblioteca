# Eres un experto programador en Python orientado a objetos, por tanto desarrola las clases necesarias que modelen un restarante, que
# tiene diferentes platos, cada plato con distintos ingredientes, el restaurante tiene muchas mesas y varias meseras


class Platos:
    def __init__(self, plato1, plato2, plato3, plato4, plato5):
        self.plato1 = plato1
        self.plato2 = plato2
        self.plato3 = plato3
        self.plato4 = plato4
        self.plato5 = plato5

    def show_menu(self):
        print("La carta es la siguiente:")
        print(f"1.- {self.plato1}")
        print(f"2.- {self.plato2}")
        print(f"3.- {self.plato3}")
        print(f"4.- {self.plato4}")
        print(f"5.- {self.plato5}")

    def ingredientes(self):
        choose = input("Elija el plato que desea: ")
        if choose == self.plato1:
            print(
                "Los ingredientes son: ingrediente1.1, ingrediente1.2, ingrediente1.3"
            )
        elif choose == self.plato2:
            print(
                "Los ingredientes son: ingrediente2.1, ingrediente2.2, ingrediente2.3"
            )
        elif choose == self.plato3:
            print(
                "Los ingredientes son: ingrediente3.1, ingrediente3.2, ingrediente3.3"
            )
        elif choose == self.plato4:
            print(
                "Los ingredientes son: ingrediente4.1, ingrediente4.2, ingrediente4.3"
            )
        elif choose == self.plato5:
            print(
                "Los ingredientes son: ingrediente5.1, ingrediente5.2, ingrediente5.3"
            )
        else:
            print("Su opción no es válida")


class Servicio:
    def __init__(self, mesera1, mesera2, mesera3, mesera4):
        self.mesera1 = mesera1
        self.mesera2 = mesera2
        self.mesera3 = mesera3
        self.mesera4 = mesera4

    def mesa(self):
        choose_table = int(input("Escoja el número de mesa (del 1 al 8): "))
        print(f"La mesa escogida es {choose_table}")

    def mesera(self):
        choose_waitress = int(
            input("Escoja a la mesera que le atenderá (del 1 al 4): ")
        )
        if choose_waitress == 1:
            return self.mesera1
        elif choose_waitress == 2:
            return self.mesera2
        elif choose_waitress == 3:
            return self.mesera3
        elif choose_waitress == 4:
            return self.mesera4
        else:
            print("Su opción no es válida")


carta = Platos(
    "ceviche", "pachamanca", "lomo saltado", "tallarines verdes", "pollo a la brasa"
)
carta.show_menu()
carta.ingredientes()

servicio = Servicio("Maria", "Luciana", "Ana", "Lucía")
servicio.mesa()
print(f"La mesera que le atenderá es {servicio.mesera()}")
