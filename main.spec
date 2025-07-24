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
datas += collect_data_files('pandas')

# Collect hidden imports
hiddenimports = [
    'eventlet.hubs.epolls',
    'eventlet.hubs.kqueue', 
    'eventlet.hubs.selects',
    'eventlet.hubs.poll',
    'eventlet.hubs.hub',
    'eventlet.green.threading',
    'eventlet.green.time',
    'eventlet.green.socket',
    'eventlet.green.ssl',
    'eventlet.wsgi',
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
    'pyproj._datadir',
    'pandas',
    'pandas._libs.tslib',
    'pandas._libs.algos',
    'pandas._libs.join',
    'pandas._libs.lib',
    'pandas._libs.hashtable',
    'pandas._libs.ops',
    'pandas._libs.index',
    'pandas._libs.sparse',
    'pandas._libs.interval',
    'pandas._libs.writers',
    'pandas._libs.parsers',
    'pandas._libs.testing',
    'pandas._libs.reduction',
    'pandas._libs.groupby',
    'pandas._libs.window',
    'pandas._libs.reshape',
    'openpyxl',
    'xlsxwriter',
    'io',
    'threading',
    'logging',
    'datetime',
    'json',
    'time',
    'os',
    'webbrowser'
]

# Add all socketio and eventlet submodules
hiddenimports.extend(collect_submodules('socketio'))
hiddenimports.extend(collect_submodules('eventlet'))
hiddenimports.extend(collect_submodules('dns'))

# Add specific eventlet modules that might be missing
hiddenimports.extend([
    'eventlet.green.dns',
    'eventlet.support.greendns',
])

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
