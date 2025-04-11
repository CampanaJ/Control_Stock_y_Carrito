import sqlite3
import os
from datetime import datetime
from fpdf import FPDF
import webbrowser
import pandas as pd

RUTA_BD = "stock.db"
RUTA_IMAGENES = "imagenes"

if not os.path.exists(RUTA_IMAGENES):
    os.makedirs(RUTA_IMAGENES)

def nombre_archivo(base, extension, carpeta="Exportaciones"):
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    fecha = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    nombre = f"{base}_{fecha}.{extension}"
    return os.path.join(carpeta, nombre)

def conectar():
    return sqlite3.connect(RUTA_BD)

def inicializar_db():
    con = conectar()
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            imagen TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descripcion TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            nombre TEXT,
            cantidad INTEGER,
            precio_unitario REAL,
            total REAL,
            fecha TEXT
        )
    ''')
    con.commit()
    con.close()

def agregar_historial(tipo, descripcion):
    con = conectar()
    cur = con.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO historial (fecha, tipo, descripcion) VALUES (?, ?, ?)", (fecha, tipo, descripcion))
    con.commit()
    con.close()

def agregar_producto(nombre, descripcion, precio, cantidad, imagen):
    con = conectar()
    cur = con.cursor()
    imagen_nombre = os.path.basename(imagen) if imagen else None
    if imagen:
        ruta_destino = os.path.join(RUTA_IMAGENES, imagen_nombre)
        if not os.path.exists(ruta_destino):
            with open(imagen, 'rb') as fsrc, open(ruta_destino, 'wb') as fdst:
                fdst.write(fsrc.read())
    cur.execute("INSERT INTO productos (nombre, descripcion, precio, cantidad, imagen) VALUES (?, ?, ?, ?, ?)",
                (nombre, descripcion, precio, cantidad, imagen_nombre))
    con.commit()
    con.close()
    agregar_historial("Ingreso", f"Producto agregado: {nombre}")

def modificar_producto(id_producto, nombre, descripcion, precio, cantidad, imagen):
    con = conectar()
    cur = con.cursor()
    if imagen:
        imagen_nombre = os.path.basename(imagen)
        ruta_destino = os.path.join(RUTA_IMAGENES, imagen_nombre)
        if not os.path.exists(ruta_destino):
            with open(imagen, 'rb') as fsrc, open(ruta_destino, 'wb') as fdst:
                fdst.write(fsrc.read())
        cur.execute("""UPDATE productos SET nombre=?, descripcion=?, precio=?, cantidad=?, imagen=? WHERE id=?""",
                    (nombre, descripcion, precio, cantidad, imagen_nombre, id_producto))
    else:
        cur.execute("""UPDATE productos SET nombre=?, descripcion=?, precio=?, cantidad=? WHERE id=?""",
                    (nombre, descripcion, precio, cantidad, id_producto))
    con.commit()
    con.close()
    agregar_historial("Modificación", f"Producto modificado: {nombre}")

def eliminar_producto(id_producto):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT nombre FROM productos WHERE id=?", (id_producto,))
    nombre = cur.fetchone()[0]
    cur.execute("DELETE FROM productos WHERE id=?", (id_producto,))
    con.commit()
    con.close()
    agregar_historial("Eliminación", f"Producto eliminado: {nombre}")

def vender_producto(id_producto, cantidad):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT nombre, cantidad, precio FROM productos WHERE id=?", (id_producto,))
    producto = cur.fetchone()
    if not producto:
        con.close()
        return False, "Producto no encontrado"
    nombre, stock_actual, precio_unitario = producto
    if cantidad > stock_actual:
        con.close()
        return False, "Stock insuficiente"
    nuevo_stock = stock_actual - cantidad
    cur.execute("UPDATE productos SET cantidad=? WHERE id=?", (nuevo_stock, id_producto))
    total = round(precio_unitario * cantidad, 2)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""INSERT INTO ventas (producto_id, nombre, cantidad, precio_unitario, total, fecha)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (id_producto, nombre, cantidad, precio_unitario, total, fecha))
    con.commit()
    con.close()
    agregar_historial("Venta", f"{cantidad} unidad(es) de {nombre} vendidas por ${total:.2f}")
    return True, "Venta realizada"

def registrar_venta(id_producto, cantidad):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT nombre, cantidad, precio FROM productos WHERE id=?", (id_producto,))
    producto = cur.fetchone()
    if not producto:
        con.close()
        return
    nombre, stock_actual, precio_unitario = producto
    nuevo_stock = stock_actual - cantidad
    cur.execute("UPDATE productos SET cantidad=? WHERE id=?", (nuevo_stock, id_producto))
    total = round(precio_unitario * cantidad, 2)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""INSERT INTO ventas (producto_id, nombre, cantidad, precio_unitario, total, fecha)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (id_producto, nombre, cantidad, precio_unitario, total, fecha))
    con.commit()
    con.close()
    agregar_historial("Venta", f"{cantidad} unidad(es) de {nombre} vendidas por ${total:.2f}")

def obtener_productos(filtro=""):
    con = conectar()
    cur = con.cursor()
    if filtro:
        cur.execute("""SELECT id, nombre, descripcion, precio, cantidad, precio * cantidad AS total, imagen
                       FROM productos WHERE nombre LIKE ? OR descripcion LIKE ?""", (f"%{filtro}%", f"%{filtro}%"))
    else:
        cur.execute("""SELECT id, nombre, descripcion, precio, cantidad, precio * cantidad AS total, imagen
                       FROM productos""")
    productos = cur.fetchall()
    con.close()
    return productos

def buscar_producto_por_id(id_producto):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos WHERE id=?", (id_producto,))
    producto = cur.fetchone()
    con.close()
    return producto

def obtener_historial():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM historial ORDER BY fecha DESC")
    historial = cur.fetchall()
    con.close()
    return historial

def obtener_ventas():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT nombre, cantidad, precio_unitario, total, fecha FROM ventas ORDER BY fecha DESC")
    ventas = cur.fetchall()
    con.close()
    return ventas

def generar_boleta_pdf(productos, carpeta="boletas"):
    import os
    from datetime import datetime
    from fpdf import FPDF

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = f"OrdenCompra_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.pdf"
    ruta_pdf = os.path.join(carpeta, nombre_archivo)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    # Encabezado
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=10, y=8, w=30)
    pdf.set_xy(50, 10)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, "Santa Tecno", ln=True, align="R")
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Orden de Compra", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Fecha: {fecha_actual}", ln=True, align="R")
    pdf.ln(10)

    # Tabla
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 10, "Producto", border=1)
    pdf.cell(30, 10, "Precio", border=1, align="R")
    pdf.cell(30, 10, "Cantidad", border=1, align="R")
    pdf.cell(40, 10, "Subtotal", border=1, ln=True, align="R")

    pdf.set_font("Arial", size=12)
    total_general = 0
    for prod in productos:
        subtotal = prod["precio"] * prod["cantidad"]
        total_general += subtotal
        pdf.cell(80, 10, prod["nombre"], border=1)
        pdf.cell(30, 10, f"${prod['precio']:.2f}", border=1, align="R")
        pdf.cell(30, 10, str(prod["cantidad"]), border=1, align="R")
        pdf.cell(40, 10, f"${subtotal:.2f}", border=1, ln=True, align="R")

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Total", border=1)
    pdf.cell(40, 10, f"${total_general:.2f}", border=1, ln=True, align="R")

    # Guardar el PDF (sin abrirlo automáticamente)
    pdf.output(ruta_pdf)

    return ruta_pdf