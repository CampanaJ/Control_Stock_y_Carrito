import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
from ttkbootstrap import Style
import platform
import logica
from exportaciones import (
    exportar_productos_excel, exportar_productos_pdf,
    exportar_historial_excel, exportar_historial_pdf
)
from carrito import CarritoVentana


def abrir_archivo(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            os.system(f"open '{path}'")
        else:
            os.system(f"xdg-open '{path}'")
    except Exception as e:
        messagebox.showwarning("Atención", f"Archivo generado en:\n{path}\n\n(No se pudo abrir automáticamente)\n\n{e}")


class InterfazApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Santa Tecno - Control de Stock")
        self.style = Style("cyborg")
        self.tema_actual = "cyborg"

        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        self.centrar_ventana(self.root)

        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.nombre_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        self.precio_var = tk.DoubleVar(value=0.0)
        self.cantidad_var = tk.IntVar(value=0)
        self.busqueda_var = tk.StringVar()
        self.imagen_path = None

        self.crear_widgets()
        logica.inicializar_db()
        self.actualizar_tabla()
        self.ver_historial()
        self.ver_historial()

    def centrar_ventana(self, ventana):
        ventana.update_idletasks()
        ancho = ventana.winfo_width()
        alto = ventana.winfo_height()
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f"+{x}+{y}")

    def crear_widgets(self):
        notebook = ttk.Notebook(self.root)
        self.tab_productos = ttk.Frame(notebook, padding=10)
        self.tab_historial = ttk.Frame(notebook, padding=10)
        notebook.add(self.tab_productos, text="\U0001F4E6 Productos")
        notebook.add(self.tab_historial, text="\U0001F4DC Historial")
        notebook.pack(fill="both", expand=True)

        self.crear_tab_productos()
        self.crear_tab_historial()

    def crear_tab_productos(self):
        frame_entrada = ttk.Labelframe(self.tab_productos, text="Datos del Producto", padding=10)
        frame_entrada.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_entrada, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(frame_entrada, textvariable=self.nombre_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_entrada, text="Descripción:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ttk.Entry(frame_entrada, textvariable=self.descripcion_var, width=30).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_entrada, text="Precio:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(frame_entrada, textvariable=self.precio_var, width=15).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_entrada, text="Cantidad:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        ttk.Entry(frame_entrada, textvariable=self.cantidad_var, width=15).grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(frame_entrada, text="Seleccionar Imagen", command=self.seleccionar_imagen).grid(row=2, column=1, columnspan=2, pady=5)

        frame_botones = ttk.Frame(self.tab_productos, padding=10)
        frame_botones.pack()
        botones = [
            ("\U0001F6D2 Carrito", self.abrir_ventana_carrito),
            ("⧧ Agregar", self.agregar_producto),
            ("✎ Modificar", self.abrir_ventana_modificar),
            ("✖ Eliminar", self.eliminar_producto),
            ("➕ Agregar Stock", self.abrir_ventana_agregar_stock),
            ("\U0001F4CA Excel", self.exportar_a_excel),
            ("\U0001F4C4 PDF", self.exportar_a_pdf),
            ("\U0001F319 Tema", self.toggle_tema),
            ("\U0001F6AA Salir", self.salir_app)
        ]
        for texto, comando in botones:
            ttk.Button(frame_botones, text=texto, command=comando, width=15).pack(side="left", padx=5)

        frame_busqueda = ttk.Frame(self.tab_productos)
        frame_busqueda.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_busqueda, text="Buscar:").pack(side="left", padx=5)
        entry_buscar = ttk.Entry(frame_busqueda, textvariable=self.busqueda_var)
        entry_buscar.pack(side="left", padx=5)
        entry_buscar.bind("<Return>", lambda e: self.actualizar_tabla())
        ttk.Button(frame_busqueda, text="Buscar", command=self.actualizar_tabla).pack(side="left", padx=5)

        self.tree = ttk.Treeview(
            self.tab_productos, columns=("ID", "Nombre", "Descripción", "Precio", "Cantidad", "Total"), show="headings"
        )
        columnas = {
            "ID": 50, "Nombre": 150, "Descripción": 200,
            "Precio": 100, "Cantidad": 100, "Total": 120
        }
        for col, ancho in columnas.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.mostrar_imagen_producto)

    def abrir_ventana_agregar_stock(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Selecciona un producto", "Selecciona un producto de la lista para agregar stock.")
            return

        id_producto = self.tree.item(seleccionado)["values"][0]
        producto = logica.buscar_producto_por_id(id_producto)
        if not producto:
            messagebox.showerror("Error", "Producto no encontrado.")
            return

        cantidad = simpledialog.askinteger("Agregar Stock", f"¿Cuántas unidades desea agregar a '{producto[1]}'?", minvalue=1)
        if cantidad:
            nueva_cantidad = producto[4] + cantidad
            logica.modificar_producto(id_producto, producto[1], producto[2], producto[3], nueva_cantidad, None)
            logica.agregar_historial("Stock", f"Stock agregado: {cantidad} unidades a {producto[1]}")
            self.actualizar_tabla()
            self.ver_historial()

    def crear_tab_historial(self):
        frame_botones_historial = ttk.Frame(self.tab_historial, padding=10)
        frame_botones_historial.pack()
        botones = [
            ("\U0001F4DC Exportar Excel", self.exportar_historial_excel),
            ("\U0001F4DC Exportar PDF", self.exportar_historial_pdf)
        ]
        for texto, comando in botones:
            ttk.Button(frame_botones_historial, text=texto, command=comando).pack(side="left", padx=10)

        self.historial_texto = tk.Text(self.tab_historial, wrap="word", font=("Courier New", 10))
        self.historial_texto.pack(padx=10, pady=10, fill="both", expand=True)
        self.historial_texto.config(state="disabled")
        self.ver_historial()

    def actualizar_tabla(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        productos = logica.obtener_productos(self.busqueda_var.get())
        for p in productos:
            self.tree.insert("", "end", values=(p[0], p[1], p[2], f"${p[3]:.2f}", p[4], f"${p[5]:.2f}"))

    def ver_historial(self):
        self.historial_texto.config(state="normal")
        self.historial_texto.delete("1.0", "end")
        for h in logica.obtener_historial():
            self.historial_texto.insert("end", f"{h[1]} - {h[2]}: {h[3]}\n")
        self.historial_texto.config(state="disabled")

    def agregar_producto(self):
        if not self.nombre_var.get() or not self.descripcion_var.get():
            messagebox.showwarning("Campos incompletos", "Por favor completa todos los campos.")
            return
        try:
            logica.agregar_producto(self.nombre_var.get(), self.descripcion_var.get(),
                                    self.precio_var.get(), self.cantidad_var.get(), self.imagen_path)
            self.actualizar_tabla()
            self.ver_historial()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def abrir_ventana_modificar(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Selecciona un producto", "Selecciona un producto de la lista.")
            return

        id_producto = self.tree.item(seleccionado)["values"][0]
        producto = logica.buscar_producto_por_id(id_producto)
        if not producto:
            messagebox.showerror("Error", "Producto no encontrado.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Modificar Producto")
        ventana.geometry("600x360")
        self.centrar_ventana(ventana)
        ventana.transient(self.root)
        ventana.grab_set()

        nombre_var = tk.StringVar(value=producto[1])
        desc_var = tk.StringVar(value=producto[2])
        precio_var = tk.DoubleVar(value=producto[3])
        cantidad_var = tk.IntVar(value=producto[4])
        imagen_mod_path = [None]

        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame, textvariable=nombre_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Descripción:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame, textvariable=desc_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Precio:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame, textvariable=precio_var, width=20).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Cantidad:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame, textvariable=cantidad_var, width=20).grid(row=3, column=1, padx=5, pady=5)

        img_label = ttk.Label(frame)
        img_label.grid(row=0, column=2, rowspan=5, padx=10)

        ruta_img = os.path.join(logica.RUTA_IMAGENES, producto[5])
        if os.path.exists(ruta_img):
            img = Image.open(ruta_img).resize((120, 120))
            foto = ImageTk.PhotoImage(img)
            img_label.configure(image=foto)
            img_label.image = foto

        def seleccionar_nueva_imagen():
            path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
            if path:
                imagen_mod_path[0] = path
                img = Image.open(path).resize((120, 120))
                foto = ImageTk.PhotoImage(img)
                img_label.configure(image=foto)
                img_label.image = foto

        ttk.Button(frame, text="Seleccionar nueva imagen", command=seleccionar_nueva_imagen).grid(row=5, column=0, columnspan=2, pady=5)
        ttk.Button(frame, text="Guardar cambios", command=lambda: self.guardar_modificaciones(
            ventana, id_producto, nombre_var, desc_var, precio_var, cantidad_var, imagen_mod_path[0]), bootstyle="success").grid(row=6, column=0, columnspan=3, pady=10)

    def guardar_modificaciones(self, ventana, id_producto, nombre, desc, precio, cantidad, imagen):
        try:
            logica.modificar_producto(id_producto, nombre.get(), desc.get(), precio.get(), cantidad.get(), imagen)
            self.actualizar_tabla()
            self.ver_historial()
            ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_producto(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Selecciona un producto", "Selecciona un producto de la lista.")
            return
        id_producto = self.tree.item(seleccionado)["values"][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar producto?"):
            logica.eliminar_producto(id_producto)
            self.actualizar_tabla()
            self.ver_historial()

    def seleccionar_imagen(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
        if path:
            self.imagen_path = path

    def mostrar_imagen_producto(self, evento):
        seleccionado = self.tree.selection()
        if seleccionado:
            id_producto = self.tree.item(seleccionado)["values"][0]
            producto = logica.buscar_producto_por_id(id_producto)
            if producto and producto[5]:
                imagen_path = os.path.join(logica.RUTA_IMAGENES, producto[5])
                if os.path.exists(imagen_path):
                    ventana = tk.Toplevel(self.root)
                    ventana.title("Imagen del Producto")
                    img = Image.open(imagen_path).resize((300, 300))
                    foto = ImageTk.PhotoImage(img)
                    etiqueta = ttk.Label(ventana, image=foto)
                    etiqueta.image = foto
                    etiqueta.pack()
                    self.centrar_ventana(ventana)

    def exportar_a_excel(self):
        try:
            productos = logica.obtener_productos()
            ruta = exportar_productos_excel(productos)
            
            if ruta:
                abrir_archivo(ruta)
            else:
                messagebox.showwarning("Atención", "No se pudo generar el archivo Excel.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def exportar_a_pdf(self):
        try:
            productos = logica.obtener_productos()
            path = exportar_productos_pdf(productos, titulo="Stock de Productos")
            abrir_archivo(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def exportar_historial_excel(self):
        try:
            historial = logica.obtener_historial()
            ruta = exportar_historial_excel(historial)
            if ruta:
                abrir_archivo(ruta)
            else:
                messagebox.showwarning("Atención", "No se pudo generar el archivo Excel.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def exportar_historial_pdf(self):
        try:
            historial = logica.obtener_historial()
            ruta = exportar_historial_pdf(historial)
            if ruta:
                abrir_archivo(ruta)
            else:
                messagebox.showwarning("Atención", "No se pudo generar el PDF del historial.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_tema(self):
        nuevo_tema = "cyborg" if self.tema_actual == "flatly" else "flatly"
        self.style.theme_use(nuevo_tema)
        self.tema_actual = nuevo_tema

    def abrir_ventana_carrito(self):
        carrito_ventana = CarritoVentana(self.root)
        self.centrar_ventana(carrito_ventana)
        carrito_ventana.grab_set()

    def salir_app(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que deseas salir?"):
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazApp(root)
    root.mainloop()
