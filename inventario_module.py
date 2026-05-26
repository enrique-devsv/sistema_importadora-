import pyodbc
from datetime import datetime

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
        print("Conexión establecida con éxito.")
        return conexion

    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def agregar_producto_catalogo(cursor, sku, nombre, precio, categoria_id):
    """Inserta un nuevo producto en el catálogo."""
    try:
        query = "INSERT INTO Productos (SKU, Nombre, PrecioVentaBase, CategoriaID) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (sku, nombre, float(precio), int(categoria_id)))
        print(" Producto agregado al catálogo exitosamente.")
    except Exception as e:
        print(f" Error al insertar en la base de datos: {e}")

def ver_catalogo(cursor):
    """Devuelve la lista de productos del catálogo."""
    try:
        cursor.execute("SELECT SKU, Nombre, PrecioVentaBase FROM Productos")
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        print(f" Error al consultar el catálogo: {e}")
        return []

def registrar_ingreso_lote(cursor, id_prod, cantidad, precio_c, fecha_str):
    """Registra el ingreso de un nuevo lote de productos."""
    try:
        fecha_cad = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        
        query = """
            INSERT INTO Lotes_Inventario (ProductoID, CantidadInicial, CantidadActual, PrecioCompra, FechaCaducidad, FechaIngreso)
            VALUES (?, ?, ?, ?, ?, GETDATE())
        """
        cursor.execute(query, (int(id_prod), int(cantidad), int(cantidad), float(precio_c), fecha_cad))
        print("Lote registrado correctamente.")
    except Exception as e:
        print(f" Error al insertar en la base de datos: {e}")

def ver_inventario_disponible(cursor):
    """Devuelve el stock total disponible agrupado por producto."""
    query = """
        SELECT p.Nombre, SUM(l.CantidadActual) as Total
        FROM Productos p
        LEFT JOIN Lotes_Inventario l ON p.ID = l.ProductoID 
        GROUP BY p.Nombre
    """
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f" Error al consultar inventario: {e}")
        return []

def actualizar_precio_producto(cursor, sku, nuevo_precio):
    """Actualiza el precio base de un producto mediante su SKU."""
    try:
        query = "UPDATE Productos SET PrecioVentaBase = ? WHERE SKU = ?"
        cursor.execute(query, (float(nuevo_precio), sku))
        
        if cursor.rowcount > 0:
            print(" Precio actualizado correctamente.")
        else:
            print(f" No se encontró ningún producto con el SKU: {sku}")
    except Exception as e: