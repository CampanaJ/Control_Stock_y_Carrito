import sqlite3
import os
from datetime import datetime

RUTA_BD = "stock.db"
RUTA_IMAGENES = "imagenes"

if not os.path.exists(RUTA_IMAGENES):
    os.makedirs(RUTA_IMAGENES)

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

def obtener_productos(filtro=""):
    con = conectar()
    cur = con.cursor()
    if filtro:
        cur.execute("""
            SELECT id, nombre, descripcion, precio, cantidad, precio * cantidad AS total, imagen
            FROM productos
            WHERE nombre LIKE ? OR descripcion LIKE ?
        """, (f"%{filtro}%", f"%{filtro}%"))
    else:
        cur.execute("""
            SELECT id, nombre, descripcion, precio, cantidad, precio * cantidad AS total, imagen
            FROM productos
        """)
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
