# -*- mode: python ; coding: utf-8 -*-
import os
import sys

sys.setrecursionlimit(sys.getrecursionlimit() * 5)

BASE_DIR = os.path.abspath(".")

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[BASE_DIR],
    binaries=[],
    datas=[
        (os.path.join(BASE_DIR, 'res'), 'res'),
        (os.path.join(BASE_DIR, 'model'), 'model'),
        (os.path.join(BASE_DIR, 'config.ini'), '.'),
        (os.path.join(BASE_DIR, 'counters.json'), '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'torchvision', 'torchaudio',
        'matplotlib', 'scipy', 'pandas',
        'sklearn', 'skimage',
        'IPython', 'ipykernel', 'jupyter',
        'notebook', 'nbformat', 'nbconvert',
        'tensorboard',
        'tf2onnx', 'onnx',
        'cv2',         
        'wx', 
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
    ],
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
    name='Overwatch-Fucked-Me',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(BASE_DIR, 'res', 'build assets', 'logo.ico'),
)