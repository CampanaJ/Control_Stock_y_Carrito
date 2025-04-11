# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],  # Tu archivo principal
    pathex=['.'],
    binaries=[],
    datas=[
        ('Ico_SantaTec.ico', '.'),  # Ícono
        ('stock.db', '.'),  # Base de datos
        ('imagenes/*', 'imagenes'),  # Carpeta de imágenes
        ('exportaciones/*', 'exportaciones'),  # PDFs / Excel exportados
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SantaTecno',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Cambiá a True si querés que se vea la consola
    icon='Ico_SantaTec.ico',
    manifest='admin.manifest',  # ⚠️ Manifiesto para permisos de admin
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SantaTecno'
)
