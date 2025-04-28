; 使用 Inno Setup 脚本生成安装程序
; 文档参考：https://jrsoftware.org/ishelp/

; 定义应用程序的基本信息
#define MyAppName "pachong_gui" ; 应用程序名称
#define MyAppVersion "1.5" ; 应用程序版本
#define MyAppPublisher "shuangmian-bai" ; 发布者名称
#define MyAppURL "https://github.com/shuangmian-bai/shuangmian_pachong_gui" ; 应用程序主页
#define MyAppExeName "pachong_gui.exe" ; 主可执行文件名称

[Setup]
; 安装程序的基本设置
AppId={{44D55B28-BD93-4995-BEE5-34047FD6CD6C}} ; 应用程序唯一标识符（GUID）
AppName={#MyAppName} ; 应用程序名称
AppVersion={#MyAppVersion} ; 应用程序版本
AppPublisher={#MyAppPublisher} ; 发布者名称
AppPublisherURL={#MyAppURL} ; 发布者主页
AppSupportURL={#MyAppURL} ; 支持页面
AppUpdatesURL={#MyAppURL} ; 更新页面
DefaultDirName={autopf}\{#MyAppName} ; 默认安装路径（程序文件夹）
ArchitecturesAllowed=x64compatible ; 允许的架构（64 位兼容）
ArchitecturesInstallIn64BitMode=x64compatible ; 在 64 位模式下安装
DisableProgramGroupPage=yes ; 禁用程序组页面
PrivilegesRequiredOverridesAllowed=dialog ; 允许用户在权限不足时显示对话框
OutputDir=C:\Users\Administrator\Desktop\双面的影视爬虫带gui\安装包 ; 输出安装包的目录
OutputBaseFilename=双面的影视爬虫gui安装包 ; 输出安装包的文件名
SetupIconFile=..\static\icon\shuangmian.ico ; 安装程序的图标
Compression=lzma ; 使用 LZMA 压缩算法
SolidCompression=yes ; 启用固实压缩
WizardStyle=modern ; 使用现代向导样式

[Languages]
; 设置安装程序的语言
Name: "chinese"; MessagesFile: "compiler:Languages\Chinese.isl" ; 使用中文语言包

[Tasks]
; 定义安装任务（如创建桌面图标）
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}" ; 创建桌面图标任务

[Files]
; 定义需要安装的文件
Source: "..\dist\pachong_gui\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion ; 主可执行文件
Source: "..\dist\pachong_gui\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs ; 导入整个 dist 文件夹及其子目录

[Icons]
; 定义快捷方式
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; ; 创建开始菜单快捷方式
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon ; 创建桌面快捷方式（可选）

[Run]
; 定义安装完成后的操作
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent ; 安装完成后自动运行程序