from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
import sqlite3
from db import DB_PATH
import os

def generar_factura_pdf(id_venta, abrir=False, tamaño="ticket"):
    # Obtener datos de la venta
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT numero_factura, fecha, total, cliente, rtn_cliente FROM ventas WHERE id_venta = ?", (id_venta,))
    venta = cursor.fetchone()
    conn.close()

    if not venta:
        raise Exception("No se encontró la venta.")

    numero_factura, fecha, total, cliente, rtn_cliente = venta

    # Definir tamaño de página y carpeta de salida
    output_dir = os.path.expanduser("~/Documents/Restaurante/Facturas")
    os.makedirs(output_dir, exist_ok=True)
    if tamaño == "ticket":
        ancho = 80 * mm
        alto = 297 * mm
        nombre_archivo = os.path.join(output_dir, f"ticket_{id_venta}.pdf")
    elif tamaño == "carta":
        ancho, alto = letter
        nombre_archivo = os.path.join(output_dir, f"factura_carta_{id_venta}.pdf")
    else:
        raise ValueError("Tamaño no válido: debe ser 'ticket' o 'carta'")

    # Crear PDF
    c = canvas.Canvas(nombre_archivo, pagesize=(ancho, alto))

    if tamaño == "ticket":
        y = alto - 20
        c.setFont("Helvetica", 9)
        c.drawString(10, y, f"Factura #{numero_factura}")
        y -= 15
        c.drawString(10, y, f"Fecha: {fecha}")
        y -= 15
        c.drawString(10, y, f"Cliente: {cliente}")
        y -= 15
        c.drawString(10, y, f"RTN: {rtn_cliente or ''}")
        y -= 15
        c.drawString(10, y, f"Total: L {total:.2f}")

    elif tamaño == "carta":
        y = alto - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"FACTURA #{numero_factura}")
        y -= 25
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Fecha: {fecha}")
        y -= 20
        c.drawString(50, y, f"Cliente: {cliente}")
        y -= 20
        c.drawString(50, y, f"RTN: {rtn_cliente or ''}")
        y -= 20
        c.drawString(50, y, f"Total: L {total:.2f}")

    c.showPage()
    c.save()

    if abrir:
        os.startfile(nombre_archivo)
