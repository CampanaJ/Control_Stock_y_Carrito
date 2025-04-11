; Script de instalación para Santa Tecno

[Setup]
AppName=Santa Tecno
AppVersion=1.0
DefaultDirName={autopf}\Santa Tecno
DefaultGroupName=Santa Tecno
UninstallDisplayIcon={app}\main.exe
OutputDir=dist_installer
OutputBaseFilename=SantaTecno_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "Ico_SantaTec.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Santa Tecno"; Filename: "{app}\run_as_admin.vbs"; WorkingDir: "{app}"; IconFilename: "{app}\Ico_SantaTec.ico"
Name: "{commondesktop}\Santa Tecno"; Filename: "{app}\run_as_admin.vbs"; WorkingDir: "{app}"; IconFilename: "{app}\Ico_SantaTec.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Iconos adicionales:"; Flags: checkedonce

[Run]
Filename: "wscript.exe"; Parameters: """{app}\run_as_admin.vbs"""; WorkingDir: "{app}"; Description: "Ejecutar Santa Tecno"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  VbsFile: string;
  VbsContent: string;
begin
  if CurStep = ssPostInstall then
  begin
    VbsFile := ExpandConstant('{app}\run_as_admin.vbs');
    VbsContent :=
      'Set UAC = CreateObject("Shell.Application")' + #13#10 +
      'UAC.ShellExecute "' + ExpandConstant('{app}\main.exe') + '", "", "", "runas", 1';
    SaveStringToFile(VbsFile, VbsContent, False);
  end;
end;
