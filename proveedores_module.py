from db_connection import get_connection


def crear_proveedor(nombre_empresa, pais, contacto, telefono):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO Proveedores (NombreEmpresa, Pais, ContactoPrincipal, Telefono)
    VALUES (?, ?, ?, ?)
    """

    try:
        cursor.execute(query, (nombre_empresa, pais, contacto, telefono))
        conn.commit()
        print("✅ Proveedor creado correctamente")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        conn.close()


def obtener_proveedores():
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM Proveedores"
    filas = cursor.execute(query).fetchall()

    if not filas:
        print("❌ No hay proveedores")
    else:
        for fila in filas:
            print(f"ID: {fila[0]}, Empresa: {fila[1]}, País: {fila[2]}, Contacto: {fila[3]}, Tel: {fila[4]}")

    conn.close()


def obtener_proveedor_por_id(proveedor_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM Proveedores WHERE ProveedorID = ?"
    fila = cursor.execute(query, (proveedor_id,)).fetchone()

    if not fila:
        print("❌ Proveedor no encontrado")
    else:
        print(f"ID: {fila[0]}, Empresa: {fila[1]}, País: {fila[2]}, Contacto: {fila[3]}, Tel: {fila[4]}")

    conn.close()


def actualizar_proveedor(proveedor_id, nombre_empresa, pais, contacto, telefono):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE Proveedores
    SET NombreEmpresa = ?, Pais = ?, ContactoPrincipal = ?, Telefono = ?
    WHERE ProveedorID = ?
    """

    try:
        cursor.execute(query, (nombre_empresa, pais, contacto, telefono, proveedor_id))
        conn.commit()

        if cursor.rowcount == 0:
            print(" ❌ Proveedor no encontrado")
        else:
            print(" ✅ Proveedor actualizado")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        conn.close()


def eliminar_proveedor(proveedor_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "DELETE FROM Proveedores WHERE ProveedorID = ?"

    try:
        cursor.execute(query, (proveedor_id,))
        conn.commit()

        if cursor.rowcount == 0:
            print(" ❌ No se encontró el proveedor")
        else:
            print(" ✅ Proveedor eliminado")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        conn.close()