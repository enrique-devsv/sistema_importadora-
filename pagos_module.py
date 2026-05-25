import pyodbc
from datetime import datetime

class PagosModule:
    def __init__(self, connection_string):
        self.conn_str = connection_string

    def _get_connection(self):
        return pyodbc.connect(self.conn_str)

    def registrar_pago(self, factura_id, metodo_pago_id, monto):
        """
        Registra un pago normal (Efectivo o Tarjeta) para una factura.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # 1. Validar que la factura exista y obtener su total
            cursor.execute("SELECT Total, ClienteID FROM Facturas WHERE FacturaID = ?", (factura_id,))
            factura = cursor.fetchone()
            if not factura:
                return {"status": "error", "message": f"La factura {factura_id} no existe."}
            
            total_factura = factura[0]
            cliente_id = factura[1]

            # 2. Validar que no se pague de más (o controlar si hay pagos parciales anteriores)
            cursor.execute("SELECT ISNULL(SUM(MontoPagado), 0) FROM Pagos WHERE FacturaID = ?", (factura_id,))
            total_pagado_anterior = cursor.fetchone()[0]

            if total_pagado_anterior + monto > total_factura:
                monto_restante = total_factura - total_pagado_anterior
                return {
                    "status": "error", 
                    "message": f"El monto excede el saldo restante. Saldo actual por pagar: ${monto_restante:.2f}"
                }

            # 3. Registrar el pago
            cursor.execute("""
                INSERT INTO Pagos (FacturaID, MetodoPagoID, MontoPagado, FechaPago)
                VALUES (?, ?, ?, GETDATE())
            """, (factura_id, metodo_pago_id, monto))

            # 4. Actualizar los puntos de lealtad del cliente (usando el SP existente) si la factura queda liquidada
            if (total_pagado_anterior + monto) >= total_factura:
                cursor.execute("EXEC CalcularPuntosLealtad @ClienteID = ?", (cliente_id,))
                # Leemos el resultado del SP para obtener el nuevo estatus del cliente
                puntos_actuales = cursor.fetchone()
                msg = f"Pago registrado. ¡Factura liquidada por completo! El cliente ahora tiene {puntos_actuales[0]} puntos ({puntos_actuales[1]})."
            else:
                msg = f"Pago parcial registrado. Restan: ${(total_factura - (total_pagado_anterior + monto)):.2f}"

            conn.commit()
            return {"status": "success", "message": msg}

        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": f"Error al procesar el pago: {str(e)}"}
        finally:
            conn.close()

    def registrar_pago_con_puntos(self, factura_id, puntos_a_usar):
        """
        Permite pagar utilizando los puntos acumulados del cliente.
        Regla de negocio: 1 punto = $0.10 USD de descuento.
        """
        VALOR_PUNTO = 0.10  # 10 puntos = $1.00 USD
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # 1. Obtener datos de la factura y del cliente
            cursor.execute("""
                SELECT f.Total, f.ClienteID, c.PuntosLealtad 
                FROM Facturas f 
                JOIN Clientes c ON f.ClienteID = c.ClienteID 
                WHERE f.FacturaID = ?
            """, (factura_id,))
            data = cursor.fetchone()
            
            if not data:
                return {"status": "error", "message": "Factura o Cliente no encontrado."}
            
            total_factura, cliente_id, puntos_disponibles = data

            if puntos_disponibles < puntos_a_usar:
                return {"status": "error", "message": f"El cliente solo tiene {puntos_disponibles} puntos disponibles."}

            # 2. Calcular equivalencia en dinero
            monto_descuento = puntos_a_usar * VALOR_PUNTO

            # 3. Validar saldo pendiente de la factura
            cursor.execute("SELECT ISNULL(SUM(MontoPagado), 0) FROM Pagos WHERE FacturaID = ?", (factura_id,))
            total_pagado_anterior = cursor.fetchone()[0]
            saldo_pendiente = total_factura - total_pagado_anterior

            # Si el descuento de los puntos es mayor que lo que debe, solo cobramos lo que debe
            if monto_descuento > saldo_pendiente:
                monto_descuento = saldo_pendiente
                puntos_a_usar = int(monto_descuento / VALOR_PUNTO)

            # ID de 'Puntos Lealtad' en Metodos_Pago es 3
            cursor.execute("""
                INSERT INTO Pagos (FacturaID, MetodoPagoID, MontoPagado, FechaPago)
                VALUES (?, 3, ?, GETDATE())
            """, (factura_id, monto_descuento))

            # 4. Deducir los puntos del cliente de forma manual en la tabla
            cursor.execute("""
                UPDATE Clientes 
                SET PuntosLealtad = PuntosLealtad - ? 
                WHERE ClienteID = ?
            """, (puntos_a_usar, cliente_id))

            conn.commit()
            return {
                "status": "success", 
                "message": f"Se canjearon {puntos_a_usar} puntos por un valor de ${monto_descuento:.2f}."
            }

        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": f"Error al procesar el pago con puntos: {str(e)}"}
        finally:
            conn.close()

    def obtener_estado_cuenta_factura(self, factura_id):
        """
        Devuelve el total, lo pagado y el desglose de métodos utilizados para una factura.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Total FROM Facturas WHERE FacturaID = ?", (factura_id,))
            factura = cursor.fetchone()
            if not factura:
                return {"status": "error", "message": "Factura no encontrada."}
            
            total = factura[0]

            cursor.execute("""
                SELECT mp.NombreMetodo, p.MontoPagado, p.FechaPago 
                FROM Pagos p
                JOIN Metodos_Pago mp ON p.MetodoPagoID = mp.MetodoPagoID
                WHERE p.FacturaID = ?
            """, (factura_id,))
            
            pagos = cursor.fetchall()
            lista_pagos = [{"metodo": r[0], "monto": float(r[1]), "fecha": str(r[2])} for r in pagos]
            total_pagado = sum(p["monto"] for p in lista_pagos)
            
            return {
                "status": "success",
                "factura_id": factura_id,
                "total_factura": float(total),
                "total_pagado": total_pagado,
                "saldo_pendiente": float(total) - total_pagado,
                "historial_pagos": lista_pagos
            }
        finally:
            conn.close()