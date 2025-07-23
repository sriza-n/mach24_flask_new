# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['/workspaces/mach24_flask_new'],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'eventlet.hubs.epolls',
        'eventlet.hubs.kqueue',
        'eventlet.hubs.selects',
        'dns',
        'dns.resolver',
        'dns.asyncresolver',
        'dns.e164',
        'engineio.async_drivers.eventlet',
        'socketio.async_drivers.eventlet',
        'pkg_resources.py2_warn',
        'flask_socketio',
        'flask_cors',
        'flask_sqlalchemy',
        'pyserial',
        'serial.tools.list_ports',
        'sqlite3',
        'pyproj',
        'pyproj.transformer',
        'pyproj.crs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mach24-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
