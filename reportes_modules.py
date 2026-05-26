# reportes_modules.py

from db_connection import get_connection
from utils import mostrar_encabezado, formatear_moneda


def reporte_ventas_totales():
    """
    Muestra el total de ventas agrupado por mes.
    Sirve para ver como van las ventas a lo largo del tiempo.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT YEAR(Fecha) AS Anio, MONTH(Fecha) AS Mes,
               COUNT(*) AS NumFacturas, SUM(Total) AS TotalVentas
        FROM Facturas
        GROUP BY YEAR(Fecha), MONTH(Fecha)
        ORDER BY Anio DESC, Mes DESC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        if not resultados:
            print("No hay datos de ventas.")
            return

        mostrar_encabezado("REPORTE DE VENTAS POR MES")
        total_general = 0
        for r in resultados:
            print(f"{r[0]}-{r[1]:02d} | Facturas: {r[2]} | Total: {formatear_moneda(r[3])}")
            total_general += r[3]

        print(f"\nTotal general: {formatear_moneda(total_general)}")

    except Exception as e:
        print(f"Error al generar reporte: {e}")
    finally:
        conn.close()


def reporte_productos_mas_vendidos():
    """
    Muestra los productos que mas se han vendido ordenados por cantidad.
    Sirve para saber cuales son los que tienen mas demanda.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT TOP 10 p.Nombre, SUM(df.Cantidad) AS TotalVendido,
               SUM(df.Cantidad * df.PrecioUnitario) AS Ingresos
        FROM Detalle_Factura df
        JOIN Productos p ON df.ProductoID = p.ProductoID
        GROUP BY p.Nombre
        ORDER BY TotalVendido DESC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        if not resultados:
            print("No hay datos de ventas por producto.")
            return

        mostrar_encabezado("TOP 10 PRODUCTOS MAS VENDIDOS")
        for i, r in enumerate(resultados, 1):
            print(f"{i}. {r[0]} | Vendidos: {r[1]} unidades | Ingresos: {formatear_moneda(r[2])}")

    except Exception as e:
        print(f"Error al generar reporte: {e}")
    finally:
        conn.close()


def reporte_clientes_frecuentes():
    """
    Muestra los clientes que mas han comprado ordenados por total gastado.
    Tambien muestra sus puntos de lealtad y nivel.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT TOP 10 c.ClienteID,
               c.Nombres + ' ' + c.Apellidos AS Cliente,
               COUNT(f.FacturaID) AS Compras,
               SUM(f.Total) AS TotalGastado,
               ISNULL(c.PuntosLealtad, 0) AS Puntos,
               ISNULL(c.NivelFidelidad, 'Sin nivel') AS Nivel
        FROM Clientes c
        JOIN Facturas f ON c.ClienteID = f.ClienteID
        GROUP BY c.ClienteID, c.Nombres, c.Apellidos, c.PuntosLealtad, c.NivelFidelidad
        ORDER BY TotalGastado DESC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        if not resultados:
            print("No hay datos de clientes.")
            return

        mostrar_encabezado("TOP 10 CLIENTES FRECUENTES")
        for r in resultados:
            print(f"ID: {r[0]} | {r[1]} | Compras: {r[2]} | Gastado: {formatear_moneda(r[3])} | Puntos: {r[4]} | Nivel: {r[5]}")

    except Exception as e:
        print(f"Error al generar reporte: {e}")
    finally:
        conn.close()


def reporte_inventario_bajo():
    """
    Muestra los productos con stock bajo (menos de 10 unidades).
    Esto nos ayuda a saber que productos necesitamos pedir pronto.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT p.ProductoID, p.SKU, p.Nombre,
               ISNULL(SUM(l.CantidadActual), 0) AS Stock
        FROM Productos p
        LEFT JOIN Lotes_Inventario l ON p.ProductoID = l.ProductoID
        GROUP BY p.ProductoID, p.SKU, p.Nombre
        HAVING ISNULL(SUM(l.CantidadActual), 0) < 10
        ORDER BY Stock ASC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        if not resultados:
            print("Todos los productos tienen stock suficiente.")
            return

        mostrar_encabezado("PRODUCTOS CON STOCK BAJO")
        for r in resultados:
            # Los que tienen 0 los marcamos como urgentes
            alerta = " ** AGOTADO **" if r[3] == 0 else ""
            print(f"ID: {r[0]} | SKU: {r[1]} | {r[2]} | Stock: {r[3]} unidades{alerta}")

    except Exception as e:
        print(f"Error al generar reporte: {e}")
    finally:
        conn.close()


def reporte_empleados_ventas():
    """
    Muestra las ventas realizadas por cada empleado.
    Para evaluar el rendimiento del equipo de ventas.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT e.EmpleadoID,
               e.Nombres + ' ' + e.Apellidos AS Empleado,
               e.Cargo,
               COUNT(f.FacturaID) AS Ventas,
               ISNULL(SUM(f.Total), 0) AS TotalVendido
        FROM Empleados e
        LEFT JOIN Facturas f ON e.EmpleadoID = f.EmpleadoID
        GROUP BY e.EmpleadoID, e.Nombres, e.Apellidos, e.Cargo
        ORDER BY TotalVendido DESC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        if not resultados:
            print("No hay datos de empleados.")
            return

        mostrar_encabezado("VENTAS POR EMPLEADO")
        for r in resultados:
            print(f"ID: {r[0]} | {r[1]} | Cargo: {r[2]} | Ventas: {r[3]} | Total: {formatear_moneda(r[4])}")

    except Exception as e:
        print(f"Error al generar reporte: {e}")
    finally:
        conn.close()


def reporte_lotes_por_vencer():
    """
    Muestra los lotes que estan proximos a caducar (30 dias o menos).
    Esto es importante para saber que productos hay que vender primero.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT l.LoteID, p.Nombre, l.CantidadActual, l.FechaCaducidad,
               DATEDIFF(DAY, GETDATE(), l.FechaCaducidad) AS DiasRestantes
        FROM Lotes_Inventario l
        JOIN Productos p ON l.ProductoID = p.ProductoID
        WHERE l.FechaCaducidad IS NOT NULL
          AND l.CantidadActual > 0
          AND DATEDIFF(DAY, GETDATE(), l.FechaCaducidad) <= 30
        ORDER BY l.FechaCaducidad ASC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        if not resultados:
            print("No hay lotes proximos a vencer.")
            return

        mostrar_encabezado("LOTES PROXIMOS A VENCER")
        for r in resultados:
            estado = "** VENCIDO **" if r[4] < 0 else f"{r[4]} dias"
            print(f"Lote #{r[0]} | {r[1]} | Cantidad: {r[2]} | Caduca: {r[3]} | {estado}")

    except Exception as e:
        print(f"Error al generar reporte: {e}")
    finally:
        conn.close()


def menu_reportes():
    """Submenu de reportes con todas las estadisticas disponibles."""
    while True:
        mostrar_encabezado("REPORTES Y ESTADISTICAS")
        print("1. Ventas totales por mes")
        print("2. Productos mas vendidos")
        print("3. Clientes mas frecuentes")
        print("4. Productos con stock bajo")
        print("5. Ventas por empleado")
        print("6. Lotes proximos a vencer")
        print("0. Regresar al menu principal")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == '1':
            reporte_ventas_totales()
        elif opcion == '2':
            reporte_productos_mas_vendidos()
        elif opcion == '3':
            reporte_clientes_frecuentes()
        elif opcion == '4':
            reporte_inventario_bajo()
        elif opcion == '5':
            reporte_empleados_ventas()
        elif opcion == '6':
            reporte_lotes_por_vencer()
        elif opcion == '0':
            break
        else:
            print("Opcion no valida.")
