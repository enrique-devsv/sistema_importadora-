#Repositorio proyecto DLP, parte de Katherine Ortiz 
# compras_module.py
import pyodbc

conexion = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;'
    'DATABASE=ImportadoraDB;'
    'Trusted_Connection=yes;'
)

cursor = conexion.cursor()


def agregar_proveedor(cursor, conexion):
    try:
        nombre = input("Nombre de la empresa: ").strip()
        pais = input("Pais: ").strip()
        contacto = input("Contacto: ").strip()
        telefono = input("Telefono: ").strip()

        if not nombre or not pais:
            print("Nombre y pais son obligatorios")
            return

        sql = "INSERT INTO Proveedores (NombreEmpresa, Pais, ContactoPrincipal, Telefono) VALUES ( ?, ?, ?, ?)"
        cursor.execute(sql, (nombre, pais, contacto, telefono))
        conexion.commit()

        print("Proveedor agregado correctamente")

    except Exception as e:
        print(f"Error al agregar proveedor: {e}")


def ver_proveedores(cursor):
    try:
        cursor.execute("SELECT * FROM Proveedores")
        proveedores = cursor.fetchall()

        if not proveedores:
            print("No hay proveedores registrados")
            return

        print("\nLista de Proveedores:")
        for p in proveedores:
            print(f"ID: {p[0]} | Empresa: {p[1]} | País: {p[2]} | Contacto: {p[3]} | Tel: {p[4]}")

    except Exception as e:
        print(f"Error al consultar proveedores: {e}")


def asignar_producto_a_proveedor(cursor, conexion):
    try:
        ProveedorID = input("ID del proveedor: ").strip()
        ProductoID = input("ID del producto: ").strip()
        CostoAcordado = input("Costo del producto: ").strip()

        if not ProveedorID.isdigit() or not ProductoID.isdigit():
            print("IDs deben ser números.")
            return

        if not CostoAcordado.replace('.', '', 1).isdigit():
            print("El costo debe ser un número válido.")
            return

        CostoAcordado = float(CostoAcordado)

        # Verificar proveedor
        cursor.execute("SELECT 1 FROM Proveedores WHERE ProveedorID = ?", (ProveedorID,))
        if not cursor.fetchone():
            print("El proveedor no existe.")
            return

        # Verificar producto
        cursor.execute("SELECT 1 FROM Productos WHERE ProductoID = ?", (ProductoID,))
        if not cursor.fetchone():
            print("El producto no existe.")
            return

        sql = """
        INSERT INTO Producto_Proveedor (ProductoID, ProveedorID, CostoAcordado)
        VALUES (?, ?, ?)
        """
        cursor.execute(sql, (ProductoID, ProveedorID, CostoAcordado))
        conexion.commit()

        print("Producto asignado correctamente")

    except Exception as e:
        print(f"Error al asignar producto: {e}")


def ver_productos_por_proveedor(cursor):
    try:
        ProveedorID = input("ID del proveedor: ").strip()

        if not ProveedorID.isdigit():
            print("El ID debe ser numérico.")
            return

        sql = """
        SELECT p.ProductoID, p.Nombre, pp.PrecioVentaBase
        FROM Producto_Proveedor pp
        JOIN Productos p ON pp.ProductoID = p.ProductoID
        WHERE pp.ProveedorID = ?
        ORDER BY p.Nombre
        """

        cursor.execute(sql, (ProveedorID,))
        resultados = cursor.fetchall()

        if not resultados:
            print("Este proveedor no tiene productos asignados.")
            return

        print(f"\nProductos del proveedor {ProveedorID}:")
        for r in resultados:
            print(f"Producto ID: {r[0]} | Nombre: {r[1]} | Costo: ${r[2]:.2f}")

    except Exception as e:
        print(f"Error al consultar productos: {e}")


print("Conexion exitosa")


     



