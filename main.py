# main.py

from db_connection import probar_conexion
from auth_module import menu_autenticacion
from clientes_module import menu_clientes
from proveedores_module import menu_proveedores
from compras_module import menu_compras
from inventario_module import menu_inventario
from ventas_module import menu_ventas
from facturacion_module import menu_facturacion
from pagos_module import menu_pagos
from reportes_modules import menu_reportes
from utils import limpiar_pantalla, pausar, mostrar_encabezado


def menu_principal(usuario):
    """
    Menu principal del sistema. Se muestra despues de iniciar sesion.
    Desde aqui se accede a todos los modulos del sistema.
    Recibe los datos del usuario logueado para mostrar su nombre.
    """
    while True:
        limpiar_pantalla()
        mostrar_encabezado("SISTEMA IMPORTADORA")
        print(f"Usuario: {usuario['nombre']}\n")

        print("1. Gestion de Clientes")
        print("2. Gestion de Proveedores")
        print("3. Gestion de Compras")
        print("4. Gestion de Inventario")
        print("5. Gestion de Ventas")
        print("6. Facturacion (Consultas)")
        print("7. Gestion de Pagos")
        print("8. Reportes y Estadisticas")
        print("0. Cerrar sesion")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == '1':
            menu_clientes()
        elif opcion == '2':
            menu_proveedores()
        elif opcion == '3':
            menu_compras()
        elif opcion == '4':
            menu_inventario()
        elif opcion == '5':
            menu_ventas()
        elif opcion == '6':
            menu_facturacion()
        elif opcion == '7':
            menu_pagos()
        elif opcion == '8':
            menu_reportes()
        elif opcion == '0':
            print("Sesion cerrada.")
            break
        else:
            print("Opcion no valida.")
            pausar()


def main():
    """
    Punto de entrada del programa.
    Primero verifica la conexion a la base de datos,
    despues muestra el login y si todo sale bien entra al menu.
    """
    limpiar_pantalla()
    print("Iniciando sistema...")
    print("Verificando conexion a la base de datos...\n")

    # Si no hay conexion ni tiene caso seguir
    if not probar_conexion():
        print("\nNo se pudo conectar a la base de datos.")
        print("Verifique que SQL Server este corriendo y que los datos de conexion sean correctos.")
        pausar()
        return

    print()

    # Ciclo de autenticacion - permite volver a intentar login despues de cerrar sesion
    while True:
        usuario = menu_autenticacion()

        if usuario is None:
            # El usuario eligio salir del sistema
            print("\nGracias por usar el sistema. Hasta luego.")
            break

        # Si el login fue exitoso, entramos al menu principal
        menu_principal(usuario)


if __name__ == "__main__":
    main()
