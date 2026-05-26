# utils.py
import os
import re


def limpiar_pantalla():
    """Limpia la consola dependiendo del sistema operativo."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    """Pausa la ejecucion hasta que el usuario presione Enter."""
    input("\nPresione Enter para continuar...")


def validar_entero(mensaje):
    """
    Pide un numero entero al usuario y lo valida.
    Si mete letras o algo raro, le vuelve a pedir.
    Retorna el numero ya convertido a int.
    """
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit() and int(valor) > 0:
            return int(valor)
        print("Entrada no valida. Ingrese un numero entero positivo.")


def validar_decimal(mensaje):
    """
    Pide un numero decimal al usuario, por ejemplo para precios o montos.
    Acepta numeros con punto decimal como 10.50
    """
    while True:
        valor = input(mensaje).strip()
        # Quitamos un solo punto para verificar si lo demas son digitos
        if valor.replace('.', '', 1).isdigit() and float(valor) > 0:
            return float(valor)
        print("Entrada no valida. Ingrese un numero positivo (ej: 25.50).")


def validar_email(email):
    """
    Verifica que el email tenga un formato mas o menos correcto.
    No es una validacion super estricta pero sirve para lo basico.
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None


def validar_telefono(telefono):
    """
    Verifica que el telefono tenga entre 7 y 15 digitos.
    Acepta guiones y espacios pero los ignora al contar.
    """
    solo_numeros = telefono.replace('-', '').replace(' ', '')
    return solo_numeros.isdigit() and 7 <= len(solo_numeros) <= 15


def formatear_moneda(monto):
    """
    Formatea un numero como moneda con signo de dolar y 2 decimales.
    Ejemplo: 1500.5 -> $1,500.50
    """
    try:
        return f"${monto:,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def confirmar_accion(mensaje):
    """
    Le pregunta al usuario si esta seguro de algo (S/N).
    Retorna True si confirma, False si cancela.
    """
    while True:
        respuesta = input(f"{mensaje} (S/N): ").strip().upper()
        if respuesta in ('S', 'SI'):
            return True
        elif respuesta in ('N', 'NO'):
            return False
        print("Responda S o N.")


def mostrar_encabezado(titulo):
    """
    Muestra un titulo con formato bonito en la consola.
    Lo usamos al inicio de cada submenu para que se vea ordenado.
    """
    largo = len(titulo) + 8
    print("\n" + "-" * largo)
    print(f"    {titulo}")
    print("-" * largo)
