import tkinter as tk
from interfaz import InterfazApp
import logica


if __name__ == "__main__":
    logica.inicializar_db()
    root = tk.Tk()
    app = InterfazApp(root)
    root.mainloop()