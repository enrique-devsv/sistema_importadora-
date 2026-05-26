import re
import os
from datetime import datetime

#Validaciones de Formato

def validar_dui(dui):
    # Formato: 8 dígitos, un guion y 1 dígito (ej: 00000000-0)
    patron = r"^\d{8}-\d{1}$"
    return re.match(patron, dui) is not None

def validar_email(email):
    # Formato de correo electrónico estándar
    patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(patron, email) is not None

# --- Formateo de Datos ---

def formatear_moneda(valor):
    # Convierte a float y formatea con $ y dos decimales
    try:
        return f"${float(valor):,.2f}"
    except:
        return "$0.00"

def formatear_fecha(fecha_sql):
    # Si viene como objeto datetime de SQL, lo formatea a DD/MM/YYYY
    if isinstance(fecha_sql, datetime):
        return fecha_sql.strftime("%d/%m/%Y")
    return str(fecha_sql)

# Control de Consola

def limpiar_pantalla():
    # Detecta si es Windows ('nt') o Linux/Mac y limpia la consola
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("\nPresione Enter para continuar...")
    