import pyodbc
SERVIDOR = '.\SQLEXPRESS'     # cambiar al nombre de su servidor local de SQL Server (no a todos les aparecera igual al mio.)
BASE_DE_DATOS = 'ImportadoraDB' # base de datos que estamos trabajando

try:
    # Usamos f-strings para inyectar las variables
    cadena_conexion = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={SERVIDOR};'
        f'DATABASE={BASE_DE_DATOS};'
        'Trusted_Connection=yes;'
    )

    conexion = pyodbc.connect(cadena_conexion)
    print("se conecto a la basde de datos")
    
    cursor = conexion.cursor()
    cursor.execute("SELECT @@VERSION;")

    resultado = cursor.fetchone()
    print("Versión de SQL Server:", resultado[0])
    print("informacion de la conexion: ")
    
    cursor.close()
    conexion.close()
    print("se cerrro la conexion a la db")
    print("prueba de conexion a base de datos exitosa")


except pyodbc.Error as e:
    print(f"Error al conectar a la base de datos {e}")
    print(f"Error {e}")
