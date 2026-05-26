# auth_module.py
import bcrypt
from db_connection import get_connection


def registrar_usuario():
    """
    Registra un nuevo usuario en la tabla Usuarios.
    Primero pide los datos, hashea la contrasena con bcrypt
    y luego la guarda en la base de datos.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return False

    cursor = conn.cursor()

    try:
        usuario = input("Ingrese su nombre de usuario: ").strip()
        contrasena = input("Ingrese su contrasena: ").strip()

        if not usuario or not contrasena:
            print("El usuario y la contrasena no pueden estar vacios.")
            return False

        # Verificar que el usuario no exista ya
        cursor.execute("SELECT 1 FROM Usuarios WHERE NombreUsuario = ?", (usuario,))
        if cursor.fetchone():
            print("Ese nombre de usuario ya existe, elija otro.")
            return False

        # Hasheamos la contrasena antes de guardarla
        hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

        # Guardamos con RolID=2 por defecto (usuario normal)
        # El admin se crea directo en la base de datos
        sql = "INSERT INTO Usuarios (NombreUsuario, ContrasenaHash, RolID) VALUES (?, ?, 2)"
        cursor.execute(sql, (usuario, hashed.decode('utf-8')))
        conn.commit()
        print("Usuario registrado correctamente.")
        return True

    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        return False

    finally:
        conn.close()


def iniciar_sesion():
    """
    Verifica las credenciales del usuario contra la base de datos.
    Compara la contrasena ingresada con el hash almacenado usando bcrypt.
    Retorna el UsuarioID y el RolID si las credenciales son correctas,
    o None si fallo el login.
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return None

    cursor = conn.cursor()

    try:
        usuario = input("Ingrese su usuario: ").strip()
        contrasena = input("Ingrese su contrasena: ").strip()

        sql = "SELECT UsuarioID, ContrasenaHash, RolID FROM Usuarios WHERE NombreUsuario = ?"
        cursor.execute(sql, (usuario,))
        resultado = cursor.fetchone()

        if not resultado:
            print("Usuario o contrasena incorrectos.")
            return None

        # Comparamos el hash guardado con lo que escribio el usuario
        hash_guardado = resultado[1]
        if bcrypt.checkpw(contrasena.encode('utf-8'), hash_guardado.encode('utf-8')):
            print(f"Bienvenido, {usuario}.")
            # Retornamos el ID y el rol para usarlos en el menu principal
            return {"usuario_id": resultado[0], "rol_id": resultado[2], "nombre": usuario}
        else:
            print("Usuario o contrasena incorrectos.")
            return None

    except Exception as e:
        print(f"Error al iniciar sesion: {e}")
        return None

    finally:
        conn.close()


def menu_autenticacion():
    """
    Menu de login/registro que se muestra al inicio del programa.
    El usuario puede iniciar sesion, registrarse o salir.
    Retorna los datos del usuario si logra autenticarse.
    """
    while True:
        print("\n--- SISTEMA IMPORTADORA ---")
        print("1. Iniciar sesion")
        print("2. Registrar nuevo usuario")
        print("0. Salir")

        opcion = input("Seleccione una opcion: ").strip()

        if opcion == '1':
            datos_usuario = iniciar_sesion()
            if datos_usuario:
                return datos_usuario

        elif opcion == '2':
            registrar_usuario()

        elif opcion == '0':
            print("Saliendo del sistema...")
            return None

        else:
            print("Opcion no valida.")
