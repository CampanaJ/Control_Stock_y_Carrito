import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
from PIL import Image, ImageTk
import os
import logica
import platform
import subprocess
from utils import generar_boleta_pdf

class CarritoVentana(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("🛒 Carrito de Compras")
        self.geometry("1000x600")
        self.style = Style(theme="darkly")
        self.configure(bg=self.style.colors.bg)

        self.carrito = {}
        self.productos = logica.obtener_productos()
        self.filtrados = self.productos

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.crear_galeria_productos()
        self.crear_panel_lateral()

    def crear_galeria_productos(self):
        frame_galeria = ttk.Frame(self)
        frame_galeria.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.buscador_var = tk.StringVar()
        entry_buscador = ttk.Entry(frame_galeria, textvariable=self.buscador_var)
        entry_buscador.pack(fill="x", padx=5, pady=5)
        self.buscador_var.trace_add("write", self.filtrar_productos)

        canvas = tk.Canvas(frame_galeria, bg=self.style.colors.bg)
        scrollbar = ttk.Scrollbar(frame_galeria, orient="vertical", command=canvas.yview)
        self.frame_productos = ttk.Frame(canvas)

        self.frame_productos.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.frame_productos, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.mostrar_productos()

    def mostrar_productos(self):
        for widget in self.frame_productos.winfo_children():
            widget.destroy()

        for i, producto in enumerate(self.filtrados):
            self.crear_card_producto(i, producto)

    def filtrar_productos(self, *args):
        texto = self.buscador_var.get().lower()
        self.filtrados = [p for p in self.productos if texto in p[1].lower()]
        self.mostrar_productos()

    def crear_card_producto(self, index, producto):
        frame = ttk.Frame(self.frame_productos, padding=10, relief="ridge", width=200)
        frame.grid(row=index // 3, column=index % 3, padx=5, pady=5, sticky="nsew")

        imagen_path = os.path.join(logica.RUTA_IMAGENES, producto[6]) if producto[6] else None
        if imagen_path and os.path.exists(imagen_path):
            img = Image.open(imagen_path).resize((100, 100))
            foto = ImageTk.PhotoImage(img)
            label_img = ttk.Label(frame, image=foto)
            label_img.image = foto
            label_img.pack()

        ttk.Label(frame, text=producto[1], font=("Segoe UI", 10, "bold")).pack()
        ttk.Label(frame, text=f"${producto[3]:.2f} | Stock: {producto[4]}").pack()

        cantidad_var = tk.IntVar(value=1)
        entry = ttk.Entry(frame, textvariable=cantidad_var, width=5)
        entry.pack(pady=5)

        ttk.Button(
            frame,
            text="🛒 Agregar",
            style="primary.Outline.TButton",
            command=lambda p=producto, c=cantidad_var: self.agregar_al_carrito(p, c.get())
        ).pack(pady=3)

    def crear_panel_lateral(self):
        self.panel = ttk.Frame(self, padding=10)
        self.panel.grid(row=0, column=1, sticky="nsew")

        ttk.Label(self.panel, text="🛒 Carrito", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.frame_carrito = ttk.Frame(self.panel)
        self.frame_carrito.pack(fill="both", expand=True, pady=5)

        self.label_total = ttk.Label(self.panel, text="Total: $0.00", font=("Segoe UI", 12, "bold"))
        self.label_total.pack(pady=5)

        ttk.Button(
            self.panel,
            text="💳 Finalizar Compra",
            style="success.TButton",
            command=self.finalizar_compra
        ).pack(fill="x", pady=5)

    def actualizar_carrito(self):
        for widget in self.frame_carrito.winfo_children():
            widget.destroy()

        total = 0
        for producto_id, (producto, cantidad) in self.carrito.items():
            subtotal = producto[3] * cantidad
            total += subtotal

            frame_item = ttk.Frame(self.frame_carrito)
            frame_item.pack(fill="x", pady=2)

            ttk.Label(frame_item, text=f"{producto[1]} x{cantidad}").pack(side="left")
            ttk.Label(frame_item, text=f"${subtotal:.2f}").pack(side="left", padx=5)

            ttk.Button(
                frame_item,
                text="🗑",
                width=3,
                style="danger.Outline.TButton",
                command=lambda pid=producto_id: self.quitar_producto(pid)
            ).pack(side="right")

        self.label_total.config(text=f"Total: ${total:.2f}")

    def agregar_al_carrito(self, producto, cantidad):
        if cantidad <= 0:
            messagebox.showwarning("Cantidad inválida", "La cantidad debe ser mayor a cero.")
            return

        if cantidad > producto[4]:
            messagebox.showwarning("Stock insuficiente", f"Solo hay {producto[4]} unidades en stock.")
            return

        if producto[0] in self.carrito:
            nueva_cantidad = self.carrito[producto[0]][1] + cantidad
            if nueva_cantidad > producto[4]:
                messagebox.showwarning("Stock insuficiente", f"No puedes agregar más de {producto[4]} unidades.")
                return
            self.carrito[producto[0]][1] = nueva_cantidad
        else:
            self.carrito[producto[0]] = [producto, cantidad]

        self.actualizar_carrito()

    def quitar_producto(self, producto_id):
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.actualizar_carrito()

    def finalizar_compra(self):
        if not self.carrito:
            messagebox.showinfo("Carrito vacío", "No hay productos en el carrito.")
            return

        productos_para_pdf = []
        for producto, cantidad in self.carrito.values():
            productos_para_pdf.append({
                "nombre": producto[1],
                "precio": producto[3],
                "cantidad": cantidad,
                "total": producto[3] * cantidad
            })
            logica.vender_producto(producto[0], cantidad)  # Actualiza stock y registra historial

        ruta_pdf = generar_boleta_pdf(productos_para_pdf)
        messagebox.showinfo("Compra finalizada", "Orden de compra generada exitosamente.")

        abrir = messagebox.askyesno("Abrir boleta", "¿Deseas abrir la boleta generada?")
        if abrir:
            try:
                if platform.system() == "Windows":
                    os.startfile(ruta_pdf)
                elif platform.system() == "Darwin":
                    subprocess.call(["open", ruta_pdf])
                else:
                    subprocess.call(["xdg-open", ruta_pdf])
            except Exception as e:
                messagebox.showerror("Error al abrir PDF", f"No se pudo abrir el PDF:\n{e}")

        self.carrito.clear()
        self.productos = logica.obtener_productos()
        self.filtrados = self.productos
        self.actualizar_carrito()
        self.mostrar_productos()
