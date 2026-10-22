; Inno Setup script. Built by packaging/build.py, which passes AppVersion, SourceDir and OutputDir.

#define AppName "Photo Batch Renamer"
#define AppExe "Photo Batch Renamer.exe"

[Setup]
AppId={{6F1B6C3E-2A9D-4C7B-9E51-8D3F0A4B7C21}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=kalatyn
AppPublisherURL=https://github.com/kalatyn/photo-batch-renamer
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
; Installs for the current user without admin rights; the user may choose "all users".
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir={#OutputDir}
OutputBaseFilename=PhotoBatchRenamer-{#AppVersion}-Windows-Setup
SetupIconFile=..\..\assets\icon.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2/max
SolidCompression=yes
CloseApplications=force
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
; After an update started from inside the app (silent mode), start the new version.
Filename: "{app}\{#AppExe}"; Flags: nowait; Check: WizardSilent
