# inventario_module.py
from db_connection import get_connection
from utils import validar_entero, validar_decimal, mostrar_encabezado, formatear_moneda


def agregar_producto_catalogo():
    """
    Inserta un nuevo producto en el catalogo (tabla Productos).
    Necesita SKU, nombre, precio base y la categoria a la que pertenece.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("AGREGAR PRODUCTO AL CATALOGO")

        # Mostramos las categorias disponibles para que sepa cual poner
        cursor.execute("SELECT CategoriaID, NombreCategoria FROM Categorias ORDER BY CategoriaID")
        categorias = cursor.fetchall()
        if categorias:
            print("\nCategorias disponibles:")
            for cat in categorias:
                print(f"  {cat[0]}. {cat[1]}")
        print()

        sku = input("SKU del producto: ").strip()
        nombre = input("Nombre del producto: ").strip()
        precio = validar_decimal("Precio de venta base: ")
        categoria_id = validar_entero("ID de la categoria: ")

        if not sku or not nombre:
            print("SKU y nombre son obligatorios.")
            return

        query = "INSERT INTO Productos (SKU, Nombre, PrecioVentaBase, CategoriaID) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (sku, nombre, precio, categoria_id))
        conn.commit()
        print("Producto agregado al catalogo exitosamente.")

    except Exception as e:
        print(f"Error al insertar producto: {e}")
    finally:
        conn.close()


def ver_catalogo():
    """
    Muestra la lista de todos los productos registrados en el catalogo.
    Incluye SKU, nombre, precio y categoria.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT p.ProductoID, p.SKU, p.Nombre, p.PrecioVentaBase, c.NombreCategoria
        FROM Productos p
        JOIN Categorias c ON p.CategoriaID = c.CategoriaID
        ORDER BY p.ProductoID
        """
        cursor.execute(query)
        productos = cursor.fetchall()

        if not productos:
            print("No hay productos en el catalogo.")
            return

        mostrar_encabezado("CATALOGO DE PRODUCTOS")
        for p in productos:
            print(f"ID: {p[0]} | SKU: {p[1]} | {p[2]} | Precio: {formatear_moneda(p[3])} | Categoria: {p[4]}")

    except Exception as e:
        print(f"Error al consultar catalogo: {e}")
    finally:
        conn.close()


def registrar_ingreso_lote():
    """
    Registra el ingreso de un nuevo lote al inventario.
    Un lote tiene cantidad, precio de compra y fecha de caducidad.
    La fecha de ingreso se pone automatica con GETDATE().
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("REGISTRAR INGRESO DE LOTE")
        producto_id = validar_entero("ID del producto: ")

        # Verificar que el producto exista
        cursor.execute("SELECT Nombre FROM Productos WHERE ProductoID = ?", (producto_id,))
        prod = cursor.fetchone()
        if not prod:
            print("El producto no existe.")
            return

        print(f"Producto: {prod[0]}")
        cantidad = validar_entero("Cantidad del lote: ")
        precio_compra = validar_decimal("Precio de compra por unidad: ")
        fecha_caducidad = input("Fecha de caducidad (YYYY-MM-DD, o Enter si no aplica): ").strip()

        # Si el producto no caduca se puede dejar en blanco
        if fecha_caducidad:
            query = """
            INSERT INTO Lotes_Inventario (ProductoID, CantidadInicial, CantidadActual, PrecioCompra, FechaCaducidad, FechaIngreso)
            VALUES (?, ?, ?, ?, ?, GETDATE())
            """
            cursor.execute(query, (producto_id, cantidad, cantidad, precio_compra, fecha_caducidad))
        else:
            query = """
            INSERT INTO Lotes_Inventario (ProductoID, CantidadInicial, CantidadActual, PrecioCompra, FechaIngreso)
            VALUES (?, ?, ?, ?, GETDATE())
            """
            cursor.execute(query, (producto_id, cantidad, cantidad, precio_compra))

        conn.commit()
        print("Lote registrado correctamente.")

    except Exception as e:
        print(f"Error al registrar lote: {e}")
    finally:
        conn.close()


def ver_inventario_disponible():
    """
    Muestra el stock total disponible agrupado por producto.
    Suma la CantidadActual de todos los lotes de cada producto.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        # Usamos ProductoID en lugar de ID porque asi se llama la columna en la tabla
        query = """
        SELECT p.ProductoID, p.Nombre, ISNULL(SUM(l.CantidadActual), 0) AS Stock
        FROM Productos p
        LEFT JOIN Lotes_Inventario l ON p.ProductoID = l.ProductoID
        GROUP BY p.ProductoID, p.Nombre
        ORDER BY p.Nombre
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        if not resultados:
            print("No hay productos registrados.")
            return

        mostrar_encabezado("INVENTARIO DISPONIBLE")
        for r in resultados:
            # Si el stock es 0, lo marcamos para que se note
            estado = " (SIN STOCK)" if r[2] == 0 else ""
            print(f"ID: {r[0]} | {r[1]} | Stock: {r[2]} unidades{estado}")

    except Exception as e:
        print(f"Error al consultar inventario: {e}")
    finally:
        conn.close()


def ver_detalle_lotes():
    """
    Muestra todos los lotes de un producto especifico.
    Sirve para ver cuales lotes tienen stock y cuales ya se agotaron.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        producto_id = validar_entero("ID del producto: ")

        query = """
        SELECT l.LoteID, l.CantidadInicial, l.CantidadActual, l.PrecioCompra,
               l.FechaIngreso, l.FechaCaducidad
        FROM Lotes_Inventario l
        WHERE l.ProductoID = ?
        ORDER BY l.FechaIngreso ASC
        """
        cursor.execute(query, (producto_id,))
        lotes = cursor.fetchall()

        if not lotes:
            print("No hay lotes registrados para este producto.")
            return

        mostrar_encabezado("DETALLE DE LOTES")
        for l in lotes:
            caducidad = l[5] if l[5] else "N/A"
            print(f"Lote: {l[0]} | Inicial: {l[1]} | Actual: {l[2]} | Costo: ${l[3]:.2f} | Ingreso: {l[4]} | Caduca: {caducidad}")

    except Exception as e:
        print(f"Error al consultar lotes: {e}")
    finally:
        conn.close()


def actualizar_precio_producto():
    """
    Actualiza el precio de venta base de un producto buscando por SKU.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        sku = input("SKU del producto: ").strip()
        if not sku:
            print("Debe ingresar un SKU.")
            return

        # Primero mostramos el producto para confirmar
        cursor.execute("SELECT Nombre, PrecioVentaBase FROM Productos WHERE SKU = ?", (sku,))
        producto = cursor.fetchone()

        if not producto:
            print(f"No se encontro un producto con SKU: {sku}")
            return

        print(f"Producto: {producto[0]} | Precio actual: {formatear_moneda(producto[1])}")
        nuevo_precio = validar_decimal("Nuevo precio: ")

        cursor.execute("UPDATE Productos SET PrecioVentaBase = ? WHERE SKU = ?", (nuevo_precio, sku))
        conn.commit()

        if cursor.rowcount > 0:
            print("Precio actualizado correctamente.")
        else:
            print("No se pudo actualizar el precio.")

    except Exception as e:
        print(f"Error al actualizar precio: {e}")
    finally:
        conn.close()


def menu_inventario():
    """Submenu para gestionar el inventario de productos y lotes."""
    while True:
        mostrar_encabezado("GESTION DE INVENTARIO")
        print("1. Agregar producto al catalogo")
        print("2. Ver catalogo de productos")
        print("3. Registrar ingreso de lote")
        print("4. Ver inventario disponible")
        print("5. Ver detalle de lotes por producto")
        print("6. Actualizar precio de producto")
        print("0. Regresar al menu principal")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == '1':
            agregar_producto_catalogo()
        elif opcion == '2':
            ver_catalogo()
        elif opcion == '3':
            registrar_ingreso_lote()
        elif opcion == '4':
            ver_inventario_disponible()
        elif opcion == '5':
            ver_detalle_lotes()
        elif opcion == '6':
            actualizar_precio_producto()
        elif opcion == '0':
            break
        else:
            print("Opcion no valida.")
