# proveedores_module.py

from db_connection import get_connection
from utils import validar_entero, confirmar_accion, mostrar_encabezado


def crear_proveedor():
    """
    Registra un nuevo proveedor en la base de datos.
    Pide nombre de empresa, pais, contacto y telefono.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("REGISTRAR NUEVO PROVEEDOR")
        nombre_empresa = input("Nombre de la empresa: ").strip()
        pais = input("Pais: ").strip()
        contacto = input("Contacto principal: ").strip()
        telefono = input("Telefono: ").strip()

        # Nombre y pais son obligatorios segun la tabla
        if not nombre_empresa or not pais:
            print("El nombre de la empresa y el pais son obligatorios.")
            return

        query = """
        INSERT INTO Proveedores (NombreEmpresa, Pais, ContactoPrincipal, Telefono)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (nombre_empresa, pais, contacto, telefono))
        conn.commit()
        print("Proveedor registrado correctamente.")

    except Exception as e:
        print(f"Error al registrar proveedor: {e}")
    finally:
        conn.close()


def obtener_proveedores():
    """Muestra todos los proveedores registrados en el sistema."""
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT ProveedorID, NombreEmpresa, Pais, ContactoPrincipal, Telefono FROM Proveedores ORDER BY ProveedorID")
        filas = cursor.fetchall()

        if not filas:
            print("No hay proveedores registrados.")
            return

        mostrar_encabezado("LISTA DE PROVEEDORES")
        for f in filas:
            print(f"ID: {f[0]} | Empresa: {f[1]} | Pais: {f[2]} | Contacto: {f[3]} | Tel: {f[4]}")

    except Exception as e:
        print(f"Error al consultar proveedores: {e}")
    finally:
        conn.close()


def obtener_proveedor_por_id():
    """Busca un proveedor especifico por su ID."""
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        proveedor_id = validar_entero("Ingrese el ID del proveedor: ")

        cursor.execute("SELECT * FROM Proveedores WHERE ProveedorID = ?", (proveedor_id,))
        fila = cursor.fetchone()

        if not fila:
            print("No se encontro el proveedor.")
        else:
            print(f"ID: {fila[0]} | Empresa: {fila[1]} | Pais: {fila[2]} | Contacto: {fila[3]} | Tel: {fila[4]}")

    except Exception as e:
        print(f"Error al buscar proveedor: {e}")
    finally:
        conn.close()


def actualizar_proveedor():
    """
    Actualiza los datos de un proveedor.
    Muestra los datos actuales y permite dejar campos en blanco
    para mantener el valor que ya tenia.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        proveedor_id = validar_entero("Ingrese el ID del proveedor a modificar: ")

        cursor.execute("SELECT NombreEmpresa, Pais, ContactoPrincipal, Telefono FROM Proveedores WHERE ProveedorID = ?", (proveedor_id,))
        actual = cursor.fetchone()

        if not actual:
            print("No se encontro el proveedor.")
            return

        print(f"\nDatos actuales: {actual[0]} | {actual[1]} | {actual[2]} | {actual[3]}")
        print("(Deje en blanco para mantener el valor actual)")

        nombre = input(f"Empresa [{actual[0]}]: ").strip() or actual[0]
        pais = input(f"Pais [{actual[1]}]: ").strip() or actual[1]
        contacto = input(f"Contacto [{actual[2]}]: ").strip() or actual[2]
        telefono = input(f"Telefono [{actual[3]}]: ").strip() or actual[3]

        query = """
        UPDATE Proveedores
        SET NombreEmpresa = ?, Pais = ?, ContactoPrincipal = ?, Telefono = ?
        WHERE ProveedorID = ?
        """
        cursor.execute(query, (nombre, pais, contacto, telefono, proveedor_id))
        conn.commit()

        if cursor.rowcount > 0:
            print("Proveedor actualizado correctamente.")
        else:
            print("No se pudo actualizar el proveedor.")

    except Exception as e:
        print(f"Error al actualizar: {e}")
    finally:
        conn.close()


def eliminar_proveedor():
    """
    Elimina un proveedor de la base de datos.
    Ojo: si tiene productos asignados puede fallar por las llaves foraneas.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        proveedor_id = validar_entero("Ingrese el ID del proveedor a eliminar: ")

        cursor.execute("SELECT NombreEmpresa FROM Proveedores WHERE ProveedorID = ?", (proveedor_id,))
        proveedor = cursor.fetchone()

        if not proveedor:
            print("No se encontro el proveedor.")
            return

        if confirmar_accion(f"Seguro que desea eliminar a {proveedor[0]}?"):
            cursor.execute("DELETE FROM Proveedores WHERE ProveedorID = ?", (proveedor_id,))
            conn.commit()

            if cursor.rowcount > 0:
                print("Proveedor eliminado correctamente.")
            else:
                print("No se pudo eliminar el proveedor.")
        else:
            print("Operacion cancelada.")

    except Exception as e:
        # Si tiene productos asignados, SQL Server va a tirar error por FK
        print(f"Error al eliminar proveedor: {e}")
    finally:
        conn.close()


def menu_proveedores():
    """Submenu para gestionar proveedores."""
    while True:
        mostrar_encabezado("GESTION DE PROVEEDORES")
        print("1. Registrar nuevo proveedor")
        print("2. Ver todos los proveedores")
        print("3. Buscar proveedor por ID")
        print("4. Actualizar proveedor")
        print("5. Eliminar proveedor")
        print("0. Regresar al menu principal")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == '1':
            crear_proveedor()
        elif opcion == '2':
            obtener_proveedores()
        elif opcion == '3':
            obtener_proveedor_por_id()
        elif opcion == '4':
            actualizar_proveedor()
        elif opcion == '5':
            eliminar_proveedor()
        elif opcion == '0':
            break
        else:
            print("Opcion no valida.")