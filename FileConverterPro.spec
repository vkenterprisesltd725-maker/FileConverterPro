# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for FileConverterPro
Builds a single standalone EXE with all dependencies bundled.
"""

import os
import sys

block_cipher = None

a = Analysis(
    ['converter.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
    ],
    hiddenimports=[
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL.JpegImagePlugin',
        'PIL.PngImagePlugin',
        'PIL.BmpImagePlugin',
        'PIL.TiffImagePlugin',
        'PIL.WebPImagePlugin',
        'PIL.GifImagePlugin',
        'PIL.IcoImagePlugin',
        'PIL.PdfImagePlugin',
        'pymupdf',
        'inspect',
        'argparse',
        'doctest',
        'difflib',
        'winreg',
        'ctypes',
        'shlex',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'unittest',
        'pydoc',
        'pdb',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FileConverterPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - GUI only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
