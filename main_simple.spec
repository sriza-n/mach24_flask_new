# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect all data files
datas = [
    (os.path.join(current_dir, 'templates'), 'templates'),
    (os.path.join(current_dir, 'static'), 'static'),
    (os.path.join(current_dir, 'requirements.txt'), '.'),
]

# Add pandas data files
try:
    datas += collect_data_files('pandas')
except Exception:
    pass

# Collect hidden imports - comprehensive list
hiddenimports = [
    # Core Python modules
    'threading',
    'logging',
    'datetime',
    'json',
    'time',
    'os',
    'io',
    'sqlite3',
    
    # Flask and related
    'flask',
    'flask_socketio',
    'flask_cors',
    'flask_sqlalchemy',
    'werkzeug',
    'jinja2',
    
    # Serial communication
    'serial',
    'serial.tools.list_ports',
    'pyserial',
    
    # Eventlet - core modules only
    'eventlet',
    'eventlet.wsgi',
    'eventlet.green',
    'eventlet.green.threading',
    'eventlet.green.time',
    'eventlet.green.socket',
    'eventlet.green.ssl',
    'eventlet.hubs',
    'eventlet.hubs.epolls',
    'eventlet.hubs.kqueue', 
    'eventlet.hubs.selects',
    'eventlet.hubs.poll',
    'eventlet.hubs.hub',
    
    # SocketIO
    'socketio',
    'engineio',
    'engineio.async_drivers.eventlet',
    
    # DNS - comprehensive
    'dns',
    'dns.resolver',
    'dns.asyncresolver',
    'dns.e164',
    'dns.dnssec',
    'dns.tsig',
    'dns.update',
    'dns.zone',
    'dns.query',
    'dns.rdatatype',
    'dns.rdataclass',
    'dns.rdata',
    'dns.rrset',
    'dns.name',
    'dns.message',
    'dns.flags',
    'dns.opcode',
    'dns.rcode',
    'dns.entropy',
    'dns.exception',
    'dns.inet',
    'dns.ipv4',
    'dns.ipv6',
    'dns.reversename',
    'dns.tokenizer',
    'dns.ttl',
    'dns.rdtypes',
    
    # Pyproj
    'pyproj',
    'pyproj.transformer',
    'pyproj.crs',
    
    # Pandas and related
    'pandas',
    'numpy',
    'openpyxl',
    'xlsxwriter',
    
    # Requests
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    
    # Other
    'pkg_resources',
]

# Try to collect submodules but don't fail if it doesn't work
try:
    hiddenimports.extend(collect_submodules('dns'))
except Exception:
    pass

a = Analysis(
    ['main.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='mach24-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mach24-server'
)
