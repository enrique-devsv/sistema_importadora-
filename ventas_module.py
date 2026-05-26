# ventas_module.py

from db_connection import get_connection
from utils import validar_entero, mostrar_encabezado, formatear_moneda


def crear_factura():
    """
    Crea el encabezado de una nueva factura.
    Necesita el ID del cliente y del empleado (vendedor).
    Retorna el ID de la factura generada para poder agregarle productos despues.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return None

    cursor = conn.cursor()

    try:
        mostrar_encabezado("NUEVA VENTA")
        cliente_id = validar_entero("ID del cliente: ")
        empleado_id = validar_entero("ID del empleado (vendedor): ")

        # Verificar que el cliente exista
        cursor.execute("SELECT Nombres, Apellidos FROM Clientes WHERE ClienteID = ?", (cliente_id,))
        cliente = cursor.fetchone()
        if not cliente:
            print("El cliente no existe.")
            return None

        # Verificar que el empleado exista
        cursor.execute("SELECT Nombres, Apellidos FROM Empleados WHERE EmpleadoID = ?", (empleado_id,))
        empleado = cursor.fetchone()
        if not empleado:
            print("El empleado no existe.")
            return None

        print(f"Cliente: {cliente[0]} {cliente[1]}")
        print(f"Vendedor: {empleado[0]} {empleado[1]}")

        # Insertamos el encabezado con total en 0 (se actualiza al agregar productos)
        # OUTPUT INSERTED nos devuelve el ID recien generado
        query = """
        INSERT INTO Facturas (ClienteID, EmpleadoID, Fecha, Total)
        OUTPUT INSERTED.FacturaID
        VALUES (?, ?, GETDATE(), 0)
        """
        cursor.execute(query, (cliente_id, empleado_id))
        factura_id = cursor.fetchone()[0]
        conn.commit()

        print(f"Factura #{factura_id} creada exitosamente.")
        return factura_id

    except Exception as e:
        print(f"Error al crear factura: {e}")
        return None
    finally:
        conn.close()


def agregar_detalle_factura():
    """
    Agrega productos a una factura existente.
    Ejecuta el SP ProcesarVentaFIFO para descontar del inventario
    usando el metodo FIFO (primero en entrar, primero en salir).
    Despues inserta el detalle y actualiza el total de la factura.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("AGREGAR PRODUCTO A FACTURA")
        factura_id = validar_entero("Numero de factura: ")
        producto_id = validar_entero("ID del producto: ")
        cantidad = validar_entero("Cantidad: ")

        # Verificar que la factura exista
        cursor.execute("SELECT 1 FROM Facturas WHERE FacturaID = ?", (factura_id,))
        if not cursor.fetchone():
            print("La factura no existe.")
            return

        # Verificar que el producto exista y obtener su precio
        cursor.execute("SELECT Nombre, PrecioVentaBase FROM Productos WHERE ProductoID = ?", (producto_id,))
        producto = cursor.fetchone()
        if not producto:
            print("El producto no existe.")
            return

        print(f"Producto: {producto[0]} | Precio: {formatear_moneda(producto[1])}")

        # Ejecutar el SP de FIFO para descontar del inventario
        # Si no hay stock suficiente el SP lanza un error
        cursor.execute("EXEC ProcesarVentaFIFO ?, ?", (producto_id, cantidad))

        # Insertar el detalle de la factura
        precio_unitario = producto[1]
        query_detalle = """
        INSERT INTO Detalle_Factura (FacturaID, ProductoID, Cantidad, PrecioUnitario)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(query_detalle, (factura_id, producto_id, cantidad, precio_unitario))

        # Recalcular el total de la factura sumando todos los subtotales
        query_total = """
        UPDATE Facturas
        SET Total = (SELECT SUM(Cantidad * PrecioUnitario) FROM Detalle_Factura WHERE FacturaID = ?)
        WHERE FacturaID = ?
        """
        cursor.execute(query_total, (factura_id, factura_id))
        conn.commit()

        print(f"Producto agregado a la factura. Subtotal: {formatear_moneda(precio_unitario * cantidad)}")

    except Exception as e:
        # Aqui puede caer el error de "No hay stock suficiente" del SP
        print(f"Error al agregar detalle: {e}")
        conn.rollback()
    finally:
        conn.close()


def ver_factura_completa():
    """
    Muestra una factura con todos sus detalles: cliente, vendedor, productos y total.
    Usa JOINs para traer los nombres en lugar de solo los IDs.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        factura_id = validar_entero("Numero de factura a consultar: ")

        query = """
        SELECT f.FacturaID, f.Fecha,
               c.Nombres + ' ' + c.Apellidos AS Cliente,
               e.Nombres + ' ' + e.Apellidos AS Vendedor,
               p.Nombre AS Producto,
               df.Cantidad, df.PrecioUnitario, df.Subtotal, f.Total
        FROM Facturas f
        JOIN Clientes c ON f.ClienteID = c.ClienteID
        JOIN Empleados e ON f.EmpleadoID = e.EmpleadoID
        JOIN Detalle_Factura df ON f.FacturaID = df.FacturaID
        JOIN Productos p ON df.ProductoID = p.ProductoID
        WHERE f.FacturaID = ?
        """
        cursor.execute(query, (factura_id,))
        filas = cursor.fetchall()

        if not filas:
            print("No se encontro la factura o no tiene productos.")
            return

        # Encabezado de la factura
        mostrar_encabezado(f"FACTURA #{filas[0][0]}")
        print(f"Fecha: {filas[0][1]}")
        print(f"Cliente: {filas[0][2]}")
        print(f"Vendedor: {filas[0][3]}")
        print("-" * 60)

        # Detalle de productos
        print(f"{'Producto':<25} {'Cant':<6} {'Precio':<12} {'Subtotal':<12}")
        print("-" * 60)
        for fila in filas:
            print(f"{str(fila[4]):<25} {str(fila[5]):<6} {formatear_moneda(fila[6]):<12} {formatear_moneda(fila[7]):<12}")

        print("-" * 60)
        print(f"TOTAL A PAGAR: {formatear_moneda(filas[0][8])}")

    except Exception as e:
        print(f"Error al consultar factura: {e}")
    finally:
        conn.close()


def listar_facturas():
    """
    Muestra un resumen de todas las facturas registradas.
    Util para buscar el numero de una factura sin saberselo de memoria.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT f.FacturaID, f.Fecha,
               c.Nombres + ' ' + c.Apellidos AS Cliente,
               f.Total
        FROM Facturas f
        JOIN Clientes c ON f.ClienteID = c.ClienteID
        ORDER BY f.FacturaID DESC
        """
        cursor.execute(query)
        facturas = cursor.fetchall()

        if not facturas:
            print("No hay facturas registradas.")
            return

        mostrar_encabezado("LISTA DE FACTURAS")
        for f in facturas:
            print(f"Factura #{f[0]} | Fecha: {f[1]} | Cliente: {f[2]} | Total: {formatear_moneda(f[3])}")

    except Exception as e:
        print(f"Error al listar facturas: {e}")
    finally:
        conn.close()


def procesar_devolucion():
    """
    Procesa la devolucion de un producto.
    Usa el SP ProcesarDevolucion que reingresa el stock al inventario
    y ajusta el total de la factura.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("PROCESAR DEVOLUCION")
        detalle_id = validar_entero("ID del detalle de factura: ")
        cantidad = validar_entero("Cantidad a devolver: ")
        motivo = input("Motivo de la devolucion: ").strip()

        if not motivo:
            motivo = "Sin motivo especificado"

        # Ejecutar el SP que se encarga de todo: reingresar stock y ajustar factura
        cursor.execute("EXEC ProcesarDevolucion ?, ?, ?", (detalle_id, cantidad, motivo))
        conn.commit()

        print("Devolucion procesada. El stock fue reintegrado y la factura ajustada.")

    except Exception as e:
        print(f"Error al procesar devolucion: {e}")
        conn.rollback()
    finally:
        conn.close()


def menu_ventas():
    """Submenu para gestionar ventas, facturas y devoluciones."""
    while True:
        mostrar_encabezado("GESTION DE VENTAS")
        print("1. Crear nueva factura")
        print("2. Agregar producto a factura")
        print("3. Ver factura completa")
        print("4. Listar todas las facturas")
        print("5. Procesar devolucion")
        print("0. Regresar al menu principal")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == '1':
            crear_factura()
        elif opcion == '2':
            agregar_detalle_factura()
        elif opcion == '3':
            ver_factura_completa()
        elif opcion == '4':
            listar_facturas()
        elif opcion == '5':
            procesar_devolucion()
        elif opcion == '0':
            break
        else:
            print("Opcion no valida.")
