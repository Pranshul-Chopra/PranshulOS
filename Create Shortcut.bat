@echo off
:: Run this ONCE (from inside the built dist\PranshulOS folder) to create
:: a desktop shortcut pointing at the compiled exe.
setlocal enabledelayedexpansion

set "APP_DIR=%~dp0"
set "VBS=%TEMP%\make_shortcut.vbs"
set "EXE_PATH=%APP_DIR%PranshulOS.exe"

if not exist "%EXE_PATH%" (
    echo Error: PranshulOS.exe not found in this folder.
    echo Make sure this .bat sits next to the built exe.
    pause
    exit /b 1
)

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS%"
echo Set objShell = CreateObject("Shell.Application") >> "%VBS%"
echo Set objDesktop = objShell.NameSpace(0) >> "%VBS%"
echo sLinkFile = objDesktop.Self.Path ^& "\PranshulOS.lnk" >> "%VBS%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS%"
echo oLink.TargetPath = "%EXE_PATH%" >> "%VBS%"
echo oLink.WorkingDirectory = "%APP_DIR%" >> "%VBS%"
echo oLink.Description = "PranshulOS" >> "%VBS%"
echo oLink.WindowStyle = 1 >> "%VBS%"
echo oLink.IconLocation = "%EXE_PATH%" >> "%VBS%"
echo oLink.Save >> "%VBS%"

cscript //nologo "%VBS%"
if %errorlevel% equ 0 (
    del "%VBS%"
    echo.
    echo Success! PranshulOS shortcut created on your Desktop.
) else (
    echo.
    echo Error creating shortcut.
    del "%VBS%"
)
pause
