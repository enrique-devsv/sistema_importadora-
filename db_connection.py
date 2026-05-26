import pyodbc 


def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=CARRANZA\\SQLEXPRESS;"
        "DATABASE=ImportadoraDB;"
        "Trusted_Connection=yes;"
    )
    return conn

# prueba real
try:
    conn = get_connection()
    print(" Conexión exitosa")
    conn.close()
except Exception as e:
    print(" Error:", e)