# PranshulOS.spec
# Build with: pyinstaller PranshulOS.spec
#
# --onedir (the default here, NOT --onefile) is deliberate:
#   --onefile unpacks to a temp folder on every launch, which is slower to
#   start and means any path resolved from __file__ at runtime lives in a
#   throwaway directory. --onedir avoids both problems and is easier to
#   debug if something's missing (you can see the actual folder contents).

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
    ],
    hiddenimports=[
        'webview.platforms.winforms',  # pywebview's Windows backend
        'plyer.platforms.win.notification',
    ],
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
