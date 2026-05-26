# clientes_module.py
from db_connection import get_connection
from utils import validar_entero, validar_email, confirmar_accion, mostrar_encabezado


def crear_cliente():
    """
    Inserta un nuevo cliente en la tabla Clientes.
    Pide los datos por consola y valida el email antes de guardar.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        mostrar_encabezado("REGISTRAR NUEVO CLIENTE")
        nombre = input("Nombres: ").strip()
        apellido = input("Apellidos: ").strip()
        email = input("Email: ").strip()
        telefono = input("Telefono: ").strip()

        # Validamos que no esten vacios los campos obligatorios
        if not nombre or not apellido:
            print("Los nombres y apellidos son obligatorios.")
            return

        # Validar formato del email si lo ingreso
        if email and not validar_email(email):
            print("El formato del email no es valido.")
            return

        query = """
        INSERT INTO Clientes (Nombres, Apellidos, Email, Telefono)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (nombre, apellido, email, telefono))
        conn.commit()
        print("Cliente registrado correctamente.")

    except Exception as e:
        print(f"Error al registrar cliente: {e}")
    finally:
        conn.close()


def obtener_clientes():
    """
    Muestra la lista completa de clientes con sus datos.
    Incluye los puntos de lealtad y nivel de fidelidad que se calculan con el SP.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        query = """
        SELECT ClienteID, Nombres, Apellidos, Email, Telefono,
               ISNULL(PuntosLealtad, 0), ISNULL(NivelFidelidad, 'Sin nivel')
        FROM Clientes
        ORDER BY ClienteID
        """
        cursor.execute(query)
        filas = cursor.fetchall()

        if not filas:
            print("No se encontraron clientes registrados.")
            return

        mostrar_encabezado("LISTA DE CLIENTES")
        for fila in filas:
            print(f"ID: {fila[0]} | {fila[1]} {fila[2]} | Email: {fila[3]} | Tel: {fila[4]} | Puntos: {fila[5]} | Nivel: {fila[6]}")

    except Exception as e:
        print(f"Error al consultar clientes: {e}")
    finally:
        conn.close()


def obtener_cliente_por_id():
    """
    Busca un cliente especifico por su ID y muestra sus datos.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        cliente_id = validar_entero("Ingrese el ID del cliente: ")

        query = """
        SELECT ClienteID, Nombres, Apellidos, Email, Telefono,
               ISNULL(PuntosLealtad, 0), ISNULL(NivelFidelidad, 'Sin nivel')
        FROM Clientes WHERE ClienteID = ?
        """
        fila = cursor.execute(query, (cliente_id,)).fetchone()

        if not fila:
            print(f"No se encontro el cliente con ID {cliente_id}.")
        else:
            print(f"ID: {fila[0]} | {fila[1]} {fila[2]} | Email: {fila[3]} | Tel: {fila[4]} | Puntos: {fila[5]} | Nivel: {fila[6]}")

    except Exception as e:
        print(f"Error al buscar cliente: {e}")
    finally:
        conn.close()


def actualizar_cliente():
    """
    Actualiza los datos de un cliente existente.
    Primero muestra los datos actuales para que el usuario sepa que esta editando.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        cliente_id = validar_entero("Ingrese el ID del cliente a modificar: ")

        # Primero verificamos que exista
        cursor.execute("SELECT Nombres, Apellidos, Email, Telefono FROM Clientes WHERE ClienteID = ?", (cliente_id,))
        actual = cursor.fetchone()

        if not actual:
            print("No se encontro un cliente con ese ID.")
            return

        print(f"\nDatos actuales: {actual[0]} {actual[1]} | {actual[2]} | {actual[3]}")
        print("(Deje en blanco para mantener el valor actual)")

        nombre = input(f"Nombres [{actual[0]}]: ").strip() or actual[0]
        apellido = input(f"Apellidos [{actual[1]}]: ").strip() or actual[1]
        email = input(f"Email [{actual[2]}]: ").strip() or actual[2]
        telefono = input(f"Telefono [{actual[3]}]: ").strip() or actual[3]

        query = """
        UPDATE Clientes
        SET Nombres = ?, Apellidos = ?, Email = ?, Telefono = ?
        WHERE ClienteID = ?
        """
        cursor.execute(query, (nombre, apellido, email, telefono, cliente_id))
        conn.commit()
        print("Cliente actualizado correctamente.")

    except Exception as e:
        print(f"Error al actualizar cliente: {e}")
    finally:
        conn.close()


def eliminar_cliente():
    """
    Elimina un cliente de la base de datos.
    Pide confirmacion antes de borrar para evitar accidentes.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        cliente_id = validar_entero("Ingrese el ID del cliente a eliminar: ")

        # Verificamos que exista antes de intentar borrar
        cursor.execute("SELECT Nombres, Apellidos FROM Clientes WHERE ClienteID = ?", (cliente_id,))
        cliente = cursor.fetchone()

        if not cliente:
            print("No se encontro un cliente con ese ID.")
            return

        if confirmar_accion(f"Seguro que desea eliminar a {cliente[0]} {cliente[1]}?"):
            cursor.execute("DELETE FROM Clientes WHERE ClienteID = ?", (cliente_id,))
            conn.commit()
            print("Cliente eliminado correctamente.")
        else:
            print("Operacion cancelada.")

    except Exception as e:
        print(f"Error al eliminar cliente: {e}")
    finally:
        conn.close()


def consultar_puntos_lealtad():
    """
    Ejecuta el SP CalcularPuntosLealtad para actualizar y mostrar
    los puntos y nivel de fidelidad de un cliente.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()

    try:
        cliente_id = validar_entero("Ingrese el ID del cliente: ")

        # Llamamos al procedimiento almacenado que calcula los puntos
        cursor.execute("EXEC CalcularPuntosLealtad ?", (cliente_id,))
        resultado = cursor.fetchone()
        conn.commit()

        if resultado:
            print(f"Puntos de lealtad: {resultado[0]}")
            print(f"Nivel de fidelidad: {resultado[1]}")
        else:
            print("No se encontro informacion del cliente.")

    except Exception as e:
        print(f"Error al consultar puntos: {e}")
    finally:
        conn.close()


def menu_clientes():
    """
    Submenu con todas las opciones disponibles para gestion de clientes.
    Desde aqui se accede al CRUD completo y a la consulta de lealtad.
    """
    while True:
        mostrar_encabezado("GESTION DE CLIENTES")
        print("1. Registrar nuevo cliente")
        print("2. Ver todos los clientes")
        print("3. Buscar cliente por ID")
        print("4. Actualizar cliente")
        print("5. Eliminar cliente")
        print("6. Consultar puntos de lealtad")
        print("0. Regresar al menu principal")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == '1':
            crear_cliente()
        elif opcion == '2':
            obtener_clientes()
        elif opcion == '3':
            obtener_cliente_por_id()
        elif opcion == '4':
            actualizar_cliente()
        elif opcion == '5':
            eliminar_cliente()
        elif opcion == '6':
            consultar_puntos_lealtad()
        elif opcion == '0':
            break
        else:
            print("Opcion no valida.")