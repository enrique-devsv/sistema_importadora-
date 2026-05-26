# facturacionmodule


def crear_factura(cursor):
    """
    Pide el ID del Cliente y el Empleado. Crea el encabezado de la factura 
    y retorna el FacturaID generado.
    """
    print("\n--- CREAR NUEVA FACTURA ---")
    cliente_id = input("Ingrese el ID del Cliente: ")
    empleado_id = input("Ingrese el ID del Empleado: ")
    
    #Consulta para insertar el encabezado y capturar el ID generado automáticamente 
    query = """
        INSERT INTO Facturas (ClienteID, EmpleadoID, Fecha) 
        OUTPUT INSERTED.FacturaID 
        VALUES (?, ?, GETDATE())
    """
    try:
        cursor.execute(query, (cliente_id, empleado_id))
        factura_id = cursor.fetchone()[0]
        print(f"¡Encabezado de factura creado con éxito! FacturaID: {factura_id}")
        return factura_id
    except Exception as e:
        print(f"Error al crear el encabezado de la factura: {e}")
        return None


def agregar_detalle_factura(cursor):
    """
    Pide FacturaID, ProductoID y Cantidad. Ejecuta el procedimiento 
    almacenado de FIFO y guarda el registro en Detalle_Factura.
    """
    print("\n--- AGREGAR DETALLE DE FACTURA ---")
    factura_id = input("Ingrese el FacturaID: ")
    producto_id = input("Ingrese el ID del Producto: ")
    cantidad = int(input("Ingrese la Cantidad a comprar: "))
    
    try:
        #Ejecución obligatoria del SP de lógica FIFO antes del insert
        cursor.execute("EXEC ProcesarVentaFIFO ?, ?", (producto_id, cantidad))
        
        #Inserción en la tabla de detalles
        query_detalle = """
            INSERT INTO Detalle_Factura (FacturaID, ProductoID, Cantidad) 
            VALUES (?, ?, ?)
        """
        cursor.execute(query_detalle, (factura_id, producto_id, cantidad))
        print("¡Detalle agregado correctamente y lógica FIFO procesada!")
    except Exception as e:
        print(f"Error al agregar detalle o procesar inventario FIFO: {e}")


def ver_factura_completa(cursor):
    """
    Pide el número de factura y realiza un SELECT con JOIN para mostrar 
    los detalles del comprador, vendedor, productos y total financiero.
    """
    print("\n--- CONSULTAR FACTURA COMPLETA ---")
    factura_id = input("Ingrese el número de factura: ")
    
    # Consulta con JOIN para unificar la información del ERP
    query = """
        SELECT 
            f.FacturaID, 
            f.Fecha,
            c.Nombres + ' ' + c.Apellidos AS Cliente,
            e.Nombres + ' ' + e.Apellidos AS Empleado,
            p.Nombre AS Producto,
            df.Cantidad,
            p.PrecioVentaBase,
            (df.Cantidad * p.PrecioVentaBase) AS SubTotal
        FROM Facturas f
        JOIN Clientes c ON f.ClienteID = c.ClienteID
        JOIN Empleados e ON f.EmpleadoID = e.EmpleadoID
        JOIN Detalle_Factura df ON f.FacturaID = df.FacturaID
        JOIN Productos p ON df.ProductoID = p.ProductoID
        WHERE f.FacturaID = ?
    """
    try:
        cursor.execute(query, (factura_id,))
        lineas_factura = cursor.fetchall()
        
        if not lineas_factura:
            print("No se encontró la factura solicitada o no posee detalles registrados.")
            return
            
        #Despliegue estético del encabezado en consola (se extrae de la primera fila)
        print("\n==================================================")
        print(f"FACTURA N°: {lineas_factura[0][0]}  |  Fecha: {lineas_factura[0][1]}")
        print(f"Cliente: {lineas_factura[0][2]}")
        print(f"Atendido por: {lineas_factura[0][3]}")
        print("--------------------------------------------------")
        print(f"{'Producto':<20} | {'Cant':<5} | {'Precio':<8} | {'Subtotal':<10}")
        print("--------------------------------------------------")
        
        #Iteración para imprimir los productos y sumar el total acumulado
        total_factura = 0.0
        for linea in lineas_factura:
            producto = linea[4]
            cantidad = linea[5]
            precio = linea[6]
            subtotal = linea[7]
            
            print(f"{producto:<20} | {cantidad:<5} | ${precio:<7.2f} | ${subtotal:<9.2f}")
            total_factura += float(subtotal)
            
        print("--------------------------------------------------")
        print(f"{'TOTAL COMPRA:':<38} ${total_factura:.2f}")
        print("==================================================\n")
        
    except Exception as e:
        print(f"Error al visualizar la factura completa: {e}")


def procesar_devolucion(cursor):
    """
    Pide el ID del Detalle de Factura, la Cantidad a devolver y el Motivo.
    Ejecuta el Procedimiento Almacenado de devoluciones.
    """
    print("\n--- PROCESAR DEVOLUCIÓN DE MERCANCÍA ---")
    detalle_id = input("Ingrese el ID del Detalle de Factura: ")
    cantidad = int(input("Ingrese la Cantidad a devolver: "))
    motivo = input("Ingrese el Motivo de la devolución: ")
    
    try:
        #Ejecución del Procedimiento Almacenado correspondiente en SQL Server
        cursor.execute("EXEC ProcesarDevolucion ?, ?, ?", (detalle_id, cantidad, motivo))
        print("¡La devolución ha sido procesada de manera exitosa!")
    except Exception as e:
        print(f"Error al ejecutar la devolución: {e}")