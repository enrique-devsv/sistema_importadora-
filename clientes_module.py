from db_connection import get_connection

def crear_cliente(nombre, apellido, email, telefono):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO Clientes (Nombres, Apellidos, Email, Telefono)
    VALUES (?, ?, ?, ?)
    """

    cursor.execute(query, (nombre, apellido, email, telefono))
    conn.commit()
    conn.close()