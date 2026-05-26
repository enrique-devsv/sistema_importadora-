# ventas_module.py

def crear_factura(cursor):
    """
    Crea el encabezado de la factura y retorna el ID generado.
    """
    print("\n--- NUEVA VENTA (ENCABEZADO) ---")
    try:
        cliente_id = int(input("Ingrese ID del Cliente: "))
        empleado_id = int(input("Ingrese ID del Empleado (Vendedor): "))
        
        # Insertar encabezado. El Total se inicializa en 0 y se actualiza con triggers o SP.
        query = """
        INSERT INTO Facturas (ClienteID, EmpleadoID, Fecha, Total) 
        OUTPUT INSERTED.FacturaID
        VALUES (?, ?, GETDATE(), 0)
        """
        cursor.execute(query, (cliente_id, empleado_id))
        
        # Obtener el ID recién generado
        factura_id = cursor.fetchone()[0]
        print(f" Factura #{factura_id} iniciada con éxito.")
        return factura_id
    except Exception as e:
        print(f" Error al crear factura: {e}")
        return None

def agregar_detalle_factura(cursor):
    """
    Agrega productos a la factura, ejecuta FIFO y registra el detalle.
    """
    print("\n--- AGREGAR PRODUCTO A FACTURA ---")
    try:
        factura_id = int(input("Ingrese el número de Factura: "))
        producto_id = int(input("Ingrese el ID del Producto: "))
        cantidad = int(input("Cantidad a comprar: "))
        
        # 1. Ejecutar el Procedimiento Almacenado de FIFO
        # Este SP verifica stock y descuenta de los lotes.
        print("Procesando salida de inventario (FIFO)...")
        cursor.execute("EXEC ProcesarVentaFIFO ?, ?", (producto_id, cantidad))
        
        # 2. Obtener el precio actual del producto para el detalle
        cursor.execute("SELECT PrecioVentaBase FROM Productos WHERE ProductoID = ?", (producto_id,))
        precio_unitario = cursor.fetchone()[0]
        
        # 3. Insertar en el detalle
        query_detalle = """
        INSERT INTO Detalle_Factura (FacturaID, ProductoID, Cantidad, PrecioUnitario)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(query_detalle, (factura_id, producto_id, cantidad, precio_unitario))
        
        # 4. Actualizar el Total de la Factura (Suma de subtotales)
        query_update_total = """
        UPDATE Facturas 
        SET Total = (SELECT SUM(Cantidad * PrecioUnitario) FROM Detalle_Factura WHERE FacturaID = ?)
        WHERE FacturaID = ?
        """
        cursor.execute(query_update_total, (factura_id, factura_id))
        
        print(f" Producto agregado. Inventario actualizado.")
    except Exception as e:
        print(f" Error al agregar detalle: {e}")

def ver_factura_completa(cursor):
    """
    Muestra la factura con datos de cliente, vendedor y lista de productos.
    """
    print("\n--- CONSULTAR FACTURA ---")
    try:
        factura_id = int(input("Ingrese el número de Factura a ver: "))
        
        # Consulta con JOINs para traer nombres en lugar de solo IDs
        query = """
        SELECT f.FacturaID, f.Fecha, c.Nombres + ' ' + c.Apellidos AS Cliente, 
               e.Nombres + ' ' + e.Apellidos AS Vendedor, p.Nombre AS Producto, 
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
        
        if filas:
            print(f"\nFactura: {filas[0][0]} | Fecha: {filas[0][1]}")
            print(f"Cliente: {filas[0][2]} | Vendedor: {filas[0][3]}")
            print("-" * 50)
            print(f"{'Producto':<20} | {'Cant':<5} | {'Precio':<10} | {'Subtotal':<10}")
            for fila in filas:
                print(f"{fila[4]:<20} | {fila[5]:<5} | ${fila[6]:<9} | ${fila[7]:<9}")
            print("-" * 50)
            print(f"TOTAL A PAGAR: ${filas[0][8]}")
        else:
            print(" No se encontró la factura o no tiene detalles.")
    except Exception as e:
        print(f" Error al visualizar factura: {e}")

def procesar_devolucion(cursor):
    """
    Ejecuta el SP de devoluciones para reintegrar stock y ajustar factura.
    """
    print("\n--- PROCESAR DEVOLUCIÓN ---")
    try:
        detalle_id = int(input("Ingrese el ID del Detalle de Factura: "))
        cantidad = int(input("Cantidad a devolver: "))
        motivo = input("Motivo de la devolución: ")
        
        # Ejecutar Procedimiento Almacenado de SQL
        cursor.execute("EXEC ProcesarDevolucion ?, ?, ?", (detalle_id, cantidad, motivo))
        
        print(" Devolución procesada. El stock ha sido reintegrado y la factura ajustada.")
    except Exception as e:
        print(f" Error en devolución: {e}")
        # solo quiero subir mi codigo a github
        
