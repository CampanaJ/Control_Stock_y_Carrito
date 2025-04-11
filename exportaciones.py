
import os
import platform
import subprocess
from datetime import datetime
import pandas as pd
from fpdf import FPDF

LOGO_PATH = "logo.png"

# ------------------ Rutas ------------------ #

def obtener_ruta_exportacion(subcarpeta):
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    ruta_base = os.path.join(escritorio, "Datos SantaTecno", subcarpeta)
    os.makedirs(ruta_base, exist_ok=True)
    return ruta_base

def nombre_archivo(tipo, extension, subcarpeta):
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    carpeta = obtener_ruta_exportacion(subcarpeta)
    return os.path.join(carpeta, f"{tipo}_{fecha}.{extension}")

def abrir_archivo(ruta):
    if ruta and os.path.exists(ruta):
        if platform.system() == "Windows":
            os.startfile(ruta)
        elif platform.system() == "Darwin":
            subprocess.call(["open", ruta])
        else:
            subprocess.call(["xdg-open", ruta])
    else:
        print(f"No se pudo abrir el archivo: {ruta}")

# ------------------ Encabezado PDF ------------------ #

def encabezado_pdf(pdf, titulo):
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=8, w=25)

    pdf.set_font("Arial", "B", 16)
    pdf.set_xy(35, 10)
    pdf.cell(0, 10, "Santa Tecno", align="R")

    pdf.set_font("Arial", "", 10)
    pdf.set_xy(35, 18)
    pdf.cell(0, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), align="R")

    pdf.ln(25)
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, titulo, ln=True, align="C", fill=True)
    pdf.ln(5)

# ------------------ Exportar Productos ------------------ #

def exportar_productos_excel(productos):
    columnas = ["ID", "Nombre", "Descripción", "Precio", "Cantidad", "Total"]
    productos_limpios = [fila[:6] for fila in productos if len(fila) >= 6]
    df = pd.DataFrame(productos_limpios, columns=columnas)
    
    ruta = nombre_archivo("productos", "xlsx", "Stock")
    if ruta is None:
        return None  # Previene errores si la ruta no se pudo generar

    df.to_excel(ruta, index=False)
    return ruta

def exportar_productos_pdf(productos, titulo=None):
    pdf = FPDF()
    pdf.add_page()
    encabezado_pdf(pdf, "Listado de Productos")

    columnas = ["ID", "Nombre", "Descripción", "Precio", "Cantidad", "Total"]
    anchos = [15, 35, 60, 25, 25, 30]

    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(200, 200, 200)
    for col, ancho in zip(columnas, anchos):
        pdf.cell(ancho, 8, col, border=1, fill=True)
    pdf.ln()

    pdf.set_font("Arial", "", 9)
    for fila in productos:
        if len(fila) >= 6:
            for i, col in enumerate(fila[:6]):
                texto = f"${col:.2f}" if i in [3, 5] else str(col)
                pdf.cell(anchos[i], 8, texto, border=1)
            pdf.ln()

    ruta = nombre_archivo("productos", "pdf", "Stock")
    pdf.output(ruta)
    return ruta

# ------------------ Exportar Historial ------------------ #

def exportar_historial_excel(historial):
    columnas = ["ID", "Fecha", "Acción", "Descripción"]
    df = pd.DataFrame(historial, columns=columnas)

    ruta = nombre_archivo("historial", "xlsx", "Historial")
    if not ruta:
        return None

    df.to_excel(ruta, index=False)
    return ruta

def exportar_historial_pdf(historial):
    if not historial:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Historial de Acciones", ln=True, align="C")
    pdf.ln(10)

    columnas = ["Fecha", "Acción", "Descripción"]
    anchos = [45, 35, 110]

    pdf.set_font("Arial", "B", 10)
    for col, ancho in zip(columnas, anchos):
        pdf.cell(ancho, 8, col, border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 9)
    for fila in historial:
        if len(fila) >= 4:
            pdf.cell(anchos[0], 8, str(fila[1]), border=1)
            pdf.cell(anchos[1], 8, str(fila[2]), border=1)
            pdf.multi_cell(anchos[2], 8, str(fila[3]), border=1)

    ruta = nombre_archivo("historial", "pdf", "Historial")
    if not ruta:
        return None

    pdf.output(ruta)
    return ruta

# ------------------ Generar Boleta ------------------ #

def generar_boleta_pdf(productos, total):
    ruta = nombre_archivo("boleta", "pdf", "Ordenes de compra")

    pdf = FPDF()
    pdf.add_page()
    encabezado_pdf(pdf, "Boleta de Venta")

    columnas = ["Nombre", "Precio", "Cantidad", "Subtotal"]
    anchos = [80, 30, 30, 40]

    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(200, 200, 200)
    for col, ancho in zip(columnas, anchos):
        pdf.cell(ancho, 8, col, border=1, fill=True)
    pdf.ln()

    pdf.set_font("Arial", "", 9)
    for p in productos:
        nombre = p.get('nombre', '')
        precio = p.get('precio', 0.0)
        cantidad = p.get('cantidad', 0)
        subtotal = precio * cantidad

        pdf.cell(anchos[0], 8, str(nombre), border=1)
        pdf.cell(anchos[1], 8, f"${precio:.2f}", border=1)
        pdf.cell(anchos[2], 8, str(cantidad), border=1)
        pdf.cell(anchos[3], 8, f"${subtotal:.2f}", border=1)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL: ${total:.2f}", ln=True, align="R")

    pdf.output(ruta)
    return ruta
