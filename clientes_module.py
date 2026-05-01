from db_connection import get_connection

CAMPOS_PERMITIDOS = {
    "Nombres": "Nombres",
    "Apellidos": "Apellidos",
    "Email": "Email",
    "Telefono": "Telefono"
}

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

    print("✅ Cliente insertado correctamente")

def obtener_cliente():
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT ClienteID, Nombres, Apellidos, Email, Telefono FROM Clientes"
    filas = cursor.execute(query).fetchall()

    if not filas:
        print("❌ No se encontraron clientes.")
    else:
        for fila in filas:
            print(f"ID: {fila[0]}, Nombre: {fila[1]}, Apellido: {fila[2]}, Email: {fila[3]}, Teléfono: {fila[4]}")
    conn.close()

def obtener_cliente_por_id(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT ClienteID, Nombres, Apellidos, Email, Telefono FROM Clientes WHERE ClienteID = ?"
    fila = cursor.execute(query, (cliente_id,)).fetchone()

    if not fila:
        print(f"❌ No se encontró el cliente con ID {cliente_id}.")
    else:
        print(f"ID: {fila[0]}, Nombre: {fila[1]}, Apellido: {fila[2]}, Email: {fila[3]}, Teléfono: {fila[4]}")
    conn.close()

def actualizar_cliente(cliente_id, nombre, apellido, email, telefono):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE Clientes
    SET Nombres = ?, Apellidos = ?, Email = ?, Telefono = ?
    WHERE ClienteID = ?
    """

    try:
        cursor.execute(query, (nombre, apellido, email, telefono, cliente_id))
        conn.commit()
        print("✅ Cliente actualizado correctamente")
    except Exception as e:
        print("❌ Error al actualizar cliente:", e)
    finally:
        conn.close()

def eliminar_cliente(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "DELETE FROM Clientes WHERE ClienteID = ?"

    try:
        cursor.execute(query, (cliente_id,))
        conn.commit()
        print("✅ Cliente eliminado correctamente")
    except Exception as e:
        print("❌ Error al eliminar cliente:", e)
    finally:
        conn.close()
                
