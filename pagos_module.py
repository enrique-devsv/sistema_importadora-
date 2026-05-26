# pagos_module.py

from db_connection import get_connection
from utils import validar_entero, validar_decimal, mostrar_encabezado, formatear_moneda, confirmar_accion


def registrar_pago():
    """
    Registra un pago asociado a una factura.
    Primero se crea el registro en la tabla Pago y despues
    se guardan los datos extras segun el metodo elegido.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("REGISTRAR PAGO")
        factura_id = validar_entero("ID de la factura: ")

        # Verificar que la factura exista y obtener su total
        cursor.execute("SELECT Total FROM Facturas WHERE FacturaID = ?", (factura_id,))
        factura = cursor.fetchone()
        if not factura:
            print("La factura no existe.")
            return

        print(f"Total de la factura: {formatear_moneda(factura[0])}")

        monto = validar_decimal("Monto a pagar: ")

        # Menu para elegir metodo de pago
        print("\nMetodos de pago disponibles:")
        print("1. Efectivo")
        print("2. Tarjeta")
        print("3. Cheque")
        print("4. Credito")

        metodo_opcion = input("Seleccione metodo de pago: ").strip()

        # Mapear la opcion al nombre del metodo
        metodos = {'1': 'Efectivo', '2': 'Tarjeta', '3': 'Cheque', '4': 'Credito'}
        metodo = metodos.get(metodo_opcion)

        if not metodo:
            print("Metodo de pago no valido.")
            return

        # Insertar el pago general y obtener su ID
        query_pago = """
        INSERT INTO Pago (FacturaID, fecha, monto, metodo, estado)
        OUTPUT INSERTED.id_Pago
        VALUES (?, GETDATE(), ?, ?, 'Completado')
        """
        cursor.execute(query_pago, (factura_id, monto, metodo))
        pago_id = cursor.fetchone()[0]

        # Segun el metodo, pedimos datos adicionales
        if metodo == 'Tarjeta':
            _registrar_tarjeta(cursor, pago_id)
        elif metodo == 'Cheque':
            _registrar_cheque(cursor, pago_id)
        elif metodo == 'Credito':
            _registrar_credito(cursor, pago_id, monto)

        conn.commit()
        print(f"Pago #{pago_id} registrado correctamente por {formatear_moneda(monto)}.")

    except Exception as e:
        print(f"Error al registrar pago: {e}")
        conn.rollback()
    finally:
        conn.close()


def _registrar_tarjeta(cursor, pago_id):
    """
    Registra los datos de pago con tarjeta (tipo, entidad y referencia).
    Esta funcion es privada, solo la llama registrar_pago.
    """
    print("\n-- Datos de la tarjeta --")
    tipo = input("Tipo (Debito/Credito): ").strip()
    entidad = input("Entidad bancaria: ").strip()
    referencia = input("Numero de referencia: ").strip()

    query = "INSERT INTO Tarjeta (id_Pago, tipo, entidad, referencia) VALUES (?, ?, ?, ?)"
    cursor.execute(query, (pago_id, tipo, entidad, referencia))


def _registrar_cheque(cursor, pago_id):
    """
    Registra los datos del cheque (banco, numero, fechas).
    """
    print("\n-- Datos del cheque --")
    banco = input("Banco: ").strip()
    numero_cheque = input("Numero de cheque: ").strip()
    fecha_emision = input("Fecha de emision (YYYY-MM-DD): ").strip()
    fecha_cobro = input("Fecha de cobro (YYYY-MM-DD): ").strip()

    query = """
    INSERT INTO Cheque (id_Pago, Banco, Numero_Cheque, Fecha_emision, Fecha_cobro)
    VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(query, (pago_id, banco, numero_cheque, fecha_emision, fecha_cobro))


def _registrar_credito(cursor, pago_id, monto):
    """
    Registra los datos del credito (cuotas, interes y saldo).
    Calcula el saldo pendiente con el interes incluido.
    """
    print("\n-- Datos del credito --")
    cuotas = validar_entero("Numero de cuotas: ")
    interes = validar_decimal("Tasa de interes (%): ")

    # Calculamos el saldo total con interes
    saldo_pendiente = monto * (1 + interes / 100)

    query = """
    INSERT INTO Credito (id_Pago, Cuota_Total, Interes, Saldo_Pendiente)
    VALUES (?, ?, ?, ?)
    """
    cursor.execute(query, (pago_id, cuotas, interes, saldo_pendiente))
    print(f"Saldo total con interes: {formatear_moneda(saldo_pendiente)}")


def ver_pagos_por_factura():
    """
    Muestra todos los pagos realizados para una factura.
    Incluye el metodo de pago y el estado.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        factura_id = validar_entero("ID de la factura: ")

        query = """
        SELECT id_Pago, fecha, monto, metodo, estado
        FROM Pago
        WHERE FacturaID = ?
        ORDER BY fecha
        """
        cursor.execute(query, (factura_id,))
        pagos = cursor.fetchall()

        if not pagos:
            print("No hay pagos registrados para esta factura.")
            return

        mostrar_encabezado(f"PAGOS DE FACTURA #{factura_id}")
        total_pagado = 0
        for p in pagos:
            print(f"Pago #{p[0]} | Fecha: {p[1]} | Monto: {formatear_moneda(p[2])} | Metodo: {p[3]} | Estado: {p[4]}")
            total_pagado += p[2]

        print(f"\nTotal pagado: {formatear_moneda(total_pagado)}")

    except Exception as e:
        print(f"Error al consultar pagos: {e}")
    finally:
        conn.close()


def ver_quedan():
    """
    Muestra los quedan pendientes (pagos a proveedores programados).
    Un quedan es como un vale de pago que se le da al proveedor.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT q.id_Quedan, q.Proveedor, q.Fecha_Vencimiento, q.estado,
               p.monto
        FROM Quedan q
        JOIN Pago p ON q.id_Pago = p.id_Pago
        ORDER BY q.Fecha_Vencimiento
        """
        cursor.execute(query)
        quedan = cursor.fetchall()

        if not quedan:
            print("No hay quedan registrados.")
            return

        mostrar_encabezado("QUEDAN PENDIENTES")
        for q in quedan:
            print(f"Quedan #{q[0]} | Proveedor: {q[1]} | Vence: {q[2]} | Estado: {q[3]} | Monto: {formatear_moneda(q[4])}")

    except Exception as e:
        print(f"Error al consultar quedan: {e}")
    finally:
        conn.close()


def menu_pagos():
    """Submenu para gestionar pagos."""
    while True:
        mostrar_encabezado("GESTION DE PAGOS")
        print("1. Registrar pago")
        print("2. Ver pagos por factura")
        print("3. Ver quedan pendientes")
        print("0. Regresar al menu principal")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == '1':
            registrar_pago()
        elif opcion == '2':
            ver_pagos_por_factura()
        elif opcion == '3':
            ver_quedan()
        elif opcion == '0':
            break
        else:
            print("Opcion no valida.")
