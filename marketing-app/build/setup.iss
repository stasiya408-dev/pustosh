#define AppName "Пустошь Маркетинг"
#define AppVer GetEnv("MKT_VERSION")
#if AppVer == ""
  #define AppVer "1.0.0"
#endif

[Setup]
AppId={{6F2A5B1E-8C3D-4E7F-9A10-5B2C7D8E9F01}
AppName={#AppName}
AppVersion={#AppVer}
AppPublisher=Пустошь
DefaultDirName={autopf}\PustoshMarketing
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=..\setup_out
OutputBaseFilename=PustoshMarketing-Setup
SetupIconFile=app.ico
UninstallDisplayIcon={app}\PustoshMarketing.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ShowLanguageDialog=no
DisableProgramGroupPage=yes
CloseApplications=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать значок на рабочем столе"; GroupDescription: "Дополнительно:"

[Files]
Source: "..\dist\PustoshMarketing\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\PustoshMarketing.exe"; Tasks: desktopicon
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\PustoshMarketing.exe"

[Run]
Filename: "{app}\PustoshMarketing.exe"; Description: "Запустить программу"; Flags: nowait postinstall skipifsilent
