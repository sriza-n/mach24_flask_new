# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os

block_cipher = None

# Collect modules
eventlet_datas, eventlet_binaries, eventlet_hiddenimports = collect_all('eventlet')
try:
    dns_datas, dns_binaries, dns_hiddenimports = collect_all('dns')
except:
    dns_datas, dns_binaries, dns_hiddenimports = [], [], []

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=eventlet_binaries + dns_binaries,
    datas=[
        ('templates', 'templates'),
        *eventlet_datas,
        *dns_datas,
    ],
    hiddenimports=[
        *eventlet_hiddenimports,
        *dns_hiddenimports,
        'dns',
        'dns.resolver',
        'dns.query',
        'dns.message',
        'dns.name',
        'dns.rdata',
        'dns.rdatatype',
        'dns.rdataclass',
        'socketio',
        'engineio', 
        'flask_socketio',
        'serial',
        'serial.tools.list_ports',
        'pyproj',
        'flask_cors',
        'sqlalchemy.dialects.sqlite',
        'socket',
        'ssl',
        'select',
        'errno',
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
    name='mach24_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)