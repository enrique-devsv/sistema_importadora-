# compras_module.py

from db_connection import get_connection
from utils import validar_entero, validar_decimal, mostrar_encabezado


def agregar_proveedor():
    """
    Registra un proveedor nuevo directamente desde el modulo de compras.
    Es un atajo para no tener que ir al menu de proveedores solo para esto.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("AGREGAR PROVEEDOR")
        nombre = input("Nombre de la empresa: ").strip()
        pais = input("Pais: ").strip()
        contacto = input("Contacto principal: ").strip()
        telefono = input("Telefono: ").strip()

        if not nombre or not pais:
            print("Nombre y pais son obligatorios.")
            return

        sql = "INSERT INTO Proveedores (NombreEmpresa, Pais, ContactoPrincipal, Telefono) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (nombre, pais, contacto, telefono))
        conn.commit()
        print("Proveedor agregado correctamente.")

    except Exception as e:
        print(f"Error al agregar proveedor: {e}")
    finally:
        conn.close()


def ver_proveedores():
    """Muestra la lista de proveedores para referencia rapida."""
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT ProveedorID, NombreEmpresa, Pais, ContactoPrincipal, Telefono FROM Proveedores ORDER BY ProveedorID")
        proveedores = cursor.fetchall()

        if not proveedores:
            print("No hay proveedores registrados.")
            return

        mostrar_encabezado("LISTA DE PROVEEDORES")
        for p in proveedores:
            print(f"ID: {p[0]} | Empresa: {p[1]} | Pais: {p[2]} | Contacto: {p[3]} | Tel: {p[4]}")

    except Exception as e:
        print(f"Error al consultar proveedores: {e}")
    finally:
        conn.close()


def asignar_producto_a_proveedor():
    """
    Crea la relacion entre un producto y un proveedor en la tabla Producto_Proveedor.
    Tambien guarda el costo acordado con ese proveedor para ese producto.
    Valida que ambos IDs existan antes de hacer el insert.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("ASIGNAR PRODUCTO A PROVEEDOR")
        proveedor_id = validar_entero("ID del proveedor: ")
        producto_id = validar_entero("ID del producto: ")
        costo = validar_decimal("Costo acordado: ")

        # Verificar que el proveedor exista en la tabla
        cursor.execute("SELECT 1 FROM Proveedores WHERE ProveedorID = ?", (proveedor_id,))
        if not cursor.fetchone():
            print("El proveedor no existe.")
            return

        # Verificar que el producto exista
        cursor.execute("SELECT 1 FROM Productos WHERE ProductoID = ?", (producto_id,))
        if not cursor.fetchone():
            print("El producto no existe.")
            return

        sql = """
        INSERT INTO Producto_Proveedor (ProductoID, ProveedorID, CostoAcordado)
        VALUES (?, ?, ?)
        """
        cursor.execute(sql, (producto_id, proveedor_id, costo))
        conn.commit()
        print("Producto asignado al proveedor correctamente.")

    except Exception as e:
        print(f"Error al asignar producto: {e}")
    finally:
        conn.close()


def ver_productos_por_proveedor():
    """
    Muestra los productos que tiene asignados un proveedor en especifico.
    Hace un JOIN entre Producto_Proveedor y Productos para traer los nombres.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        proveedor_id = validar_entero("ID del proveedor: ")

        sql = """
        SELECT p.ProductoID, p.Nombre, pp.CostoAcordado
        FROM Producto_Proveedor pp
        JOIN Productos p ON pp.ProductoID = p.ProductoID
        WHERE pp.ProveedorID = ?
        ORDER BY p.Nombre
        """
        cursor.execute(sql, (proveedor_id,))
        resultados = cursor.fetchall()

        if not resultados:
            print("Este proveedor no tiene productos asignados.")
            return

        mostrar_encabezado(f"PRODUCTOS DEL PROVEEDOR {proveedor_id}")
        for r in resultados:
            print(f"Producto ID: {r[0]} | Nombre: {r[1]} | Costo: ${r[2]:.2f}")

    except Exception as e:
        print(f"Error al consultar productos: {e}")
    finally:
        conn.close()


def menu_compras():
    """Submenu para gestionar compras y relacion producto-proveedor."""
    while True:
        mostrar_encabezado("GESTION DE COMPRAS")
        print("1. Agregar proveedor")
        print("2. Ver proveedores")
        print("3. Asignar producto a proveedor")
        print("4. Ver productos por proveedor")
        print("0. Regresar al menu principal")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == '1':
            agregar_proveedor()
        elif opcion == '2':
            ver_proveedores()
        elif opcion == '3':
            asignar_producto_a_proveedor()
        elif opcion == '4':
            ver_productos_por_proveedor()
        elif opcion == '0':
            break
        else:
            print("Opcion no valida.")
