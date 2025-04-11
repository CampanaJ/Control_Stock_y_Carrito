; Script de Inno Setup para "Santa Tecno"
[Setup]
AppName=Santa Tecno
AppVersion=1.0
DefaultDirName={autopf}\Santa Tecno
DefaultGroupName=Santa Tecno
OutputBaseFilename=Instalador_SantaTecno
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes

; Ícono del instalador y del acceso directo
SetupIconFile=Ico_SantaTec.ico

[Files]
; Ejecutable principal
Source: "dist\SantaTecno\SantaTecno.exe"; DestDir: "{app}"; Flags: ignoreversion

; Archivos y carpetas necesarios
Source: "imagenes\*"; DestDir: "{app}\imagenes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "exportaciones\*"; DestDir: "{app}\exportaciones"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "stock.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "Ico_SantaTec.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Acceso directo en escritorio con privilegios de admin
Name: "{autodesktop}\Santa Tecno"; Filename: "{app}\main.exe"; IconFilename: "{app}\Ico_SantaTec.ico"; Parameters: ""; WorkingDir: "{app}"

[Run]
; Ejecutar el programa al finalizar la instalación (opcional)
Filename: "{app}\main.exe"; Description: "Iniciar Santa Tecno"; Flags: nowait postinstall skipifsilent runascurrentuser
