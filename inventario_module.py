import pyodbc

def obtener_conexion():
    try:
    
        direccion_servidor = r'DESKTOP-VEVAGT9\SQLEXPRESS'
        base_datos = 'ImportadoraDB' 
        
        conn_str = (
            "Driver={SQL Server};"
            f"Server={direccion_servidor};"
            f"Database={base_datos};"
            "Trusted_Connection=yes;"
        )
        
        conexion = pyodbc.connect(conn_str)
        print("✅ Conexión establecida con éxito.")
        return conexion

    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None

def agregar_producto_catalogo(cursor):
    print("\n--- Registrar Producto Nuevo ---")
    sku = input("Ingrese SKU: ")
    nombre = input("Nombre del Producto: ")
    try:
        precio = float(input("Precio de Venta: "))
        categoria_id = int(input("ID de Categoría: "))
        
        query = "INSERT INTO Productos (SKU, Nombre, PrecioVentaBase, CategoriaID) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (sku, nombre, precio, categoria_id))
        print("✅ Producto agregado al catálogo exitosamente.")

    except ValueError:
        print("Error: El precio debe ser numérico y el ID de categoría un entero.")
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")


def ver_catalogo(cursor):
    print("\n--- Catálogo de Productos ---")
    cursor.execute("SELECT SKU, Nombre, PrecioVentaBase FROM Productos")
    productos = cursor.fetchall()
    if productos:
        for p in productos:
            print(f"SKU: {p[0]} | Nombre: {p[1]} | Precio: ${p[2]}")
    else:
        print("El catálogo está vacío.")

def registrar_ingreso_lote(cursor):
    print("\n--- Registrar Ingreso de Mercadería (LOTE) ---")
    try:
        id_prod = int(input("ID del Producto: "))
        cantidad = int(input("Cantidad Recibida: "))
        precio_c = float(input("Precio de Compra: "))
        fecha_cad = input("Fecha de Caducidad (AAAA-MM-DD): ")
        
        query = """
            INSERT INTO Lotes_Inventario (ProductoID, CantidadInicial, CantidadActual, PrecioCompra, FechaCaducidad, FechaIngreso)
            VALUES (?, ?, ?, ?, ?, GETDATE())
        """
        cursor.execute(query, (id_prod, cantidad, cantidad, precio_c, fecha_cad))
        print("✅ Lote registrado correctamente.")

    except ValueError:
        print("Error: El precio debe ser numérico y el ID de producto un entero.")
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")

def ver_inventario_disponible(cursor):
    print("\n--- Stock Disponible en Bodegas ---")

    query = """
        SELECT p.Nombre, SUM(l.CantidadActual) as Total
        FROM Productos p
        LEFT JOIN Lotes_Inventario l ON p.ID = l.ProductoID 
        GROUP BY p.Nombre
    """
    try:
        cursor.execute(query)
        for fila in cursor.fetchall():
            stock = fila[1] if fila[1] else 0
            print(f"Producto: {fila[0]} | Stock Total: {stock}")
    except Exception as e:
        print(f"Error al consultar inventario: {e}")

def actualizar_precio_producto(cursor):
    print("\n--- Actualizar Precio de Venta ---")
    sku = input("Ingrese el SKU del producto: ")
    try:
        nuevo_precio = float(input("Nuevo Precio: "))
        query = "UPDATE Productos SET PrecioVentaBase = ? WHERE SKU = ?"
        cursor.execute(query, (nuevo_precio, sku))
        print("✅ Precio actualizado correctamente.")
    except ValueError:
        print("❌ Error: El precio debe ser un número.")

def menu_principal():
    conexion = obtener_conexion()
    if not conexion:
        return

    cursor = conexion.cursor()

    while True:
        print("\n===============================")
        print("   SISTEMA DE INVENTARIO FIFO  ")
        print("===============================")
        print("1. Agregar producto al catálogo")
        print("2. Ver catálogo completo")
        print("3. Registrar ingreso de lote (Compra)")
        print("4. Ver stock disponible (Total)")
        print("5. Actualizar precio de venta")
        print("0. Salir")
        
        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            agregar_producto_catalogo(cursor)
            conexion.commit() 
        elif opcion == "2":
            ver_catalogo(cursor)
        elif opcion == "3":
            registrar_ingreso_lote(cursor)
            conexion.commit() 
        elif opcion == "4":
            ver_inventario_disponible(cursor)
        elif opcion == "5":
            actualizar_precio_producto(cursor)
            conexion.commit()
        elif opcion == "0":
            print("Cerrando sistema...")
            break
        else:
            print("Opción no válida.")

    cursor.close()
    conexion.close()

if __name__ == "__main__":
    menu_principal()   