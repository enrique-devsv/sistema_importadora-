from reportes_modules import menu_reportes

def main():

    while True:

        print("\n===== SISTEMA IMPORTADORA =====")
        print("1. Reportes")
        print("2. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            menu_reportes()

        elif opcion == "2":
            print("Saliendo...")
            break

        else:
            print("Opción inválida")


if __name__ == "__main__":
    main()