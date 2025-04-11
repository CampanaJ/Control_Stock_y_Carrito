# 📦 Santa Tecno - Control de Stock

Aplicación de escritorio para gestionar productos, controlar stock, generar historial y exportar reportes en PDF y Excel. Ideal para negocios o técnicos que necesitan llevar un control visual, rápido y ordenado.

---

## 🖼️ Vista previa

![Santa Tecno]
(https://imgur.com/GfB7lUH)
(https://imgur.com/K6ojWLt)
(https://imgur.com/kHUAJnX)
(https://imgur.com/8ardbig)
(https://imgur.com/bKaSEYg)
(https://imgur.com/j067yLj)
(https://imgur.com/hR7OUDy)
---

## ✨ Funcionalidades

- ✅ Agregar, modificar y eliminar productos
- ✅ Controlar cantidad de stock
- ✅ Historial de acciones (agregados, ventas, stock)
- ✅ Carrito de compras y generación de boletas en PDF
- ✅ Exportación de productos e historial a Excel y PDF
- ✅ Imágenes por producto
- ✅ Icono personalizado
- ✅ Acceso rápido y almacenamiento organizado en el escritorio

---

## 🗂️ Estructura de carpetas de exportación

Los reportes y boletas se guardan automáticamente en:

```
Escritorio/
└── Datos SantaTecno/
    ├── Stock/
    │   ├── productos_YYYY-MM-DD_HH-MM-SS.xlsx
    │   └── productos_YYYY-MM-DD_HH-MM-SS.pdf
    ├── Historial/
    │   ├── historial_YYYY-MM-DD_HH-MM-SS.xlsx
    │   └── historial_YYYY-MM-DD_HH-MM-SS.pdf
    └── Ordenes de Compra/
        └── boleta_YYYY-MM-DD_HH-MM-SS.pdf
```

---

## 🚀 Cómo ejecutar

### 🔧 Requisitos

- Python 3.10 o superior
- Librerías:
  - `tkinter`
  - `pillow`
  - `fpdf`
  - `ttkbootstrap`
  - `pandas`
  - `openpyxl`

Instalá las dependencias:

```bash
pip install -r requirements.txt
```

---

### ▶️ Ejecutar en desarrollo

```bash
python main.py
```

---

### 🛠️ Compilar en un solo `.exe`

Con PyInstaller:

```bash
pyinstaller --onefile --windowed --icon=Ico_SantaTec.ico --add-data "logo.png;." main.py
```

> ⚠️ Para permisos de administrador, usá `main.spec` incluido.

---

## 📁 Archivos principales

- `main.py` – Entrada principal de la app
- `interfaz.py` – Interfaz con Tkinter
- `carrito.py` – Ventana de carrito y compra
- `logica.py` – Lógica y acceso a base de datos
- `exportaciones.py` – Exportación de reportes y boletas
- `utils.py` – Funciones auxiliares
- `stock.db` – Base de datos SQLite
- `Ico_SantaTec.ico` – Ícono personalizado
- `logo.png` – Logo en PDF

---

## 💻 Compilación e Instalador

Usamos Inno Setup para crear un instalador `.exe` con:
- Acceso directo en escritorio
- Ejecutar como administrador

El script `setup.iss` está incluido.

---

## 📃 Licencia

Este proyecto está bajo licencia MIT.

---

> Desarrollado con 💙 para técnicos, vendedores y emprendedores que necesitan controlar su inventario de forma simple.