# PranshulOS.spec
# Build with: pyinstaller PranshulOS.spec
#
# --onedir (the default here, NOT --onefile) is deliberate:
#   --onefile unpacks to a temp folder on every launch, which is slower to
#   start and means any path resolved from __file__ at runtime lives in a
#   throwaway directory. --onedir avoids both problems and is easier to
#   debug if something's missing (you can see the actual folder contents).
#
# pywebview's Windows window backend (winforms) bridges to .NET via
# pythonnet/clr_loader. PyInstaller's default import scanning does NOT
# reliably pick up all the runtime config/DLL files pythonnet needs at
# runtime (this is a well-known, widely-reported issue across the
# pywebview/pyinstaller/pythonnet repos) — so we explicitly collect
# everything from those two packages below instead of relying on
# hiddenimports alone.

from PyInstaller.utils.hooks import collect_all

datas = [
    ('templates', 'templates'),
    ('static', 'static'),
]
binaries = []
hiddenimports = [
    'webview.platforms.winforms',
    'plyer.platforms.win.notification',
]

for pkg in ('pythonnet', 'clr_loader', 'clr'):
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
    except Exception:
        pass  # package may not exist under this exact name; safe to skip

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PranshulOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,     # no console window — this is a GUI app
    icon=None,         # point this at a .ico file if you have one, e.g. 'icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PranshulOS',
)
