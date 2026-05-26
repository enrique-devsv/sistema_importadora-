from db_connection import get_connection


def menu_reportes():

    while True:

        print("\n" + "=" * 40)
        print("       MÓDULO DE REPORTES")
        print("=" * 40)

        print("1. Ventas Totales")
        print("2. Productos Más Vendidos")
        print("3. Clientes Frecuentes")
        print("4. Cantidad de Facturas")
        print("5. Fidelización de Clientes")
        print("6. Regresar")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            reporte_ventas()

        elif opcion == "2":
            reporte_productos()

        elif opcion == "3":
            reporte_clientes()

        elif opcion == "4":
            reporte_facturas()

        elif opcion == "5":
            reporte_fidelizacion()

        elif opcion == "6":
            break

        else:
            print("\nOpción inválida")


# =====================================
# REPORTE DE VENTAS TOTALES
# =====================================

def reporte_ventas():

    try:

        conexion = get_connection()
        cursor = conexion.cursor()

        sql = """
        SELECT SUM(Total)
        FROM Facturas
        """

        cursor.execute(sql)

        resultado = cursor.fetchone()

        total = resultado[0] if resultado[0] is not None else 0

        print("\n===== VENTAS TOTALES =====")
        print(f"Total vendido: ${total:.2f}")

    except Exception as e:

        print("Error:", e)

    finally:

        conexion.close()

    input("\nPresione ENTER para continuar...")


# =====================================
# PRODUCTOS MÁS VENDIDOS
# =====================================

def reporte_productos():

    try:

        conexion = get_connection()
        cursor = conexion.cursor()

        sql = """
        SELECT
            p.Nombre,
            SUM(df.Cantidad) AS TotalVendido

        FROM Productos p

        INNER JOIN Detalle_Factura df
            ON p.ProductoID = df.ProductoID

        GROUP BY p.Nombre

        ORDER BY TotalVendido DESC
        """

        cursor.execute(sql)

        registros = cursor.fetchall()

        print("\n===== PRODUCTOS MÁS VENDIDOS =====")

        if len(registros) == 0:
            print("No existen ventas registradas.")

        else:

            for fila in registros:

                producto = fila[0]
                vendidos = fila[1]

                print(f"{producto:<30} {vendidos}")

    except Exception as e:

        print("Error:", e)

    finally:

        conexion.close()

    input("\nPresione ENTER para continuar...")


# =====================================
# CLIENTES FRECUENTES
# =====================================

def reporte_clientes():

    try:

        conexion = get_connection()
        cursor = conexion.cursor()

        sql = """
        SELECT
            c.Nombres,
            c.Apellidos,
            COUNT(f.FacturaID) AS Compras

        FROM Clientes c

        INNER JOIN Facturas f
            ON c.ClienteID = f.ClienteID

        GROUP BY
            c.Nombres,
            c.Apellidos

        ORDER BY Compras DESC
        """

        cursor.execute(sql)

        registros = cursor.fetchall()

        print("\n===== CLIENTES FRECUENTES =====")

        if len(registros) == 0:
            print("No existen compras registradas.")

        else:

            for fila in registros:

                nombre = fila[0]
                apellido = fila[1]
                compras = fila[2]

                print(f"{nombre} {apellido:<20} {compras} compras")

    except Exception as e:

        print("Error:", e)

    finally:

        conexion.close()

    input("\nPresione ENTER para continuar...")


# =====================================
# FACTURAS REGISTRADAS
# =====================================

def reporte_facturas():

    try:

        conexion = get_connection()
        cursor = conexion.cursor()

        sql = """
        SELECT COUNT(*)
        FROM Facturas
        """

        cursor.execute(sql)

        cantidad = cursor.fetchone()[0]

        print("\n===== FACTURAS REGISTRADAS =====")
        print(f"Cantidad de facturas: {cantidad}")

    except Exception as e:

        print("Error:", e)

    finally:

        conexion.close()

    input("\nPresione ENTER para continuar...")


# =====================================
# FIDELIZACIÓN DE CLIENTES
# =====================================

def reporte_fidelizacion():

    try:

        conexion = get_connection()
        cursor = conexion.cursor()

        sql = """
        SELECT
            Nombres,
            Apellidos,
            PuntosLealtad,
            NivelFidelidad

        FROM Clientes

        ORDER BY PuntosLealtad DESC
        """

        cursor.execute(sql)

        registros = cursor.fetchall()

        print("\n===== FIDELIZACIÓN DE CLIENTES =====")

        if len(registros) == 0:
            print("No existen clientes registrados.")

        else:

            for fila in registros:

                print(
                    f"{fila[0]} {fila[1]} | "
                    f"Puntos: {fila[2]} | "
                    f"Nivel: {fila[3]}"
                )

    except Exception as e:

        print("Error:", e)

    finally:

        conexion.close()

    input("\nPresione ENTER para continuar...")