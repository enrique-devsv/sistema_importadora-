# facturacion_module.py

from db_connection import get_connection
from utils import validar_entero, mostrar_encabezado, formatear_moneda


def buscar_facturas_por_cliente():
    """
    Muestra todas las facturas de un cliente en especifico.
    Util cuando un cliente quiere ver su historial de compras.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        cliente_id = validar_entero("ID del cliente: ")

        query = """
        SELECT f.FacturaID, f.Fecha, f.Total,
               e.Nombres + ' ' + e.Apellidos AS Vendedor
        FROM Facturas f
        JOIN Empleados e ON f.EmpleadoID = e.EmpleadoID
        WHERE f.ClienteID = ?
        ORDER BY f.Fecha DESC
        """
        cursor.execute(query, (cliente_id,))
        facturas = cursor.fetchall()

        if not facturas:
            print("No se encontraron facturas para este cliente.")
            return

        # Mostrar datos del cliente primero
        cursor.execute("SELECT Nombres, Apellidos FROM Clientes WHERE ClienteID = ?", (cliente_id,))
        cliente = cursor.fetchone()
        mostrar_encabezado(f"FACTURAS DE {cliente[0]} {cliente[1]}")

        total_acumulado = 0
        for f in facturas:
            print(f"Factura #{f[0]} | Fecha: {f[1]} | Total: {formatear_moneda(f[2])} | Vendedor: {f[3]}")
            total_acumulado += f[2]

        print(f"\nTotal acumulado: {formatear_moneda(total_acumulado)}")

    except Exception as e:
        print(f"Error al buscar facturas: {e}")
    finally:
        conn.close()


def buscar_facturas_por_fecha():
    """
    Busca facturas dentro de un rango de fechas.
    El formato de fecha es YYYY-MM-DD (como lo maneja SQL Server).
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("BUSCAR FACTURAS POR FECHA")
        fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ").strip()
        fecha_fin = input("Fecha fin (YYYY-MM-DD): ").strip()

        if not fecha_inicio or not fecha_fin:
            print("Debe ingresar ambas fechas.")
            return

        query = """
        SELECT f.FacturaID, f.Fecha,
               c.Nombres + ' ' + c.Apellidos AS Cliente,
               f.Total
        FROM Facturas f
        JOIN Clientes c ON f.ClienteID = c.ClienteID
        WHERE CAST(f.Fecha AS DATE) BETWEEN ? AND ?
        ORDER BY f.Fecha DESC
        """
        cursor.execute(query, (fecha_inicio, fecha_fin))
        facturas = cursor.fetchall()

        if not facturas:
            print("No se encontraron facturas en ese rango de fechas.")
            return

        total_periodo = 0
        for f in facturas:
            print(f"Factura #{f[0]} | Fecha: {f[1]} | Cliente: {f[2]} | Total: {formatear_moneda(f[3])}")
            total_periodo += f[3]

        print(f"\nTotal del periodo: {formatear_moneda(total_periodo)}")
        print(f"Cantidad de facturas: {len(facturas)}")

    except Exception as e:
        print(f"Error al buscar facturas: {e}")
    finally:
        conn.close()


def ver_devoluciones():
    """
    Muestra el historial de devoluciones registradas.
    Incluye datos de la factura original, producto y motivo.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT d.DevolucionID, f.FacturaID, p.Nombre, d.Cantidad, d.Motivo, d.Fecha
        FROM Devoluciones d
        JOIN Detalle_Factura df ON d.DetalleID = df.DetalleID
        JOIN Facturas f ON df.FacturaID = f.FacturaID
        JOIN Productos p ON df.ProductoID = p.ProductoID
        ORDER BY d.Fecha DESC
        """
        cursor.execute(query)
        devoluciones = cursor.fetchall()

        if not devoluciones:
            print("No hay devoluciones registradas.")
            return

        mostrar_encabezado("HISTORIAL DE DEVOLUCIONES")
        for d in devoluciones:
            fecha = d[5] if d[5] else "Sin fecha"
            print(f"Dev #{d[0]} | Factura #{d[1]} | Producto: {d[2]} | Cant: {d[3]} | Motivo: {d[4]} | Fecha: {fecha}")

    except Exception as e:
        print(f"Error al consultar devoluciones: {e}")
    finally:
        conn.close()


def menu_facturacion():
    """Submenu para consultas avanzadas de facturacion."""
    while True:
        mostrar_encabezado("FACTURACION - CONSULTAS")
        print("1. Buscar facturas por cliente")
        print("2. Buscar facturas por fecha")
        print("3. Ver historial de devoluciones")
        print("0. Regresar al menu principal")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == '1':
            buscar_facturas_por_cliente()
        elif opcion == '2':
            buscar_facturas_por_fecha()
        elif opcion == '3':
            ver_devoluciones()
        elif opcion == '0':
            break
        else:
            print("Opcion no valida.")
