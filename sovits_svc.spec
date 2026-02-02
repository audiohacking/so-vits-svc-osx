# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for SoVitsSVC (macOS)

import sys
from pathlib import Path

# Import PyInstaller utilities for collecting binaries and data files
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs
import os

block_cipher = None

# Determine paths
spec_root = Path(SPECPATH)
configs_dir = spec_root / 'configs'
icon_path = spec_root / 'build' / 'macos' / 'SoVitsSVC.icns'

# Collect data files for various ML libraries
print("[SoVitsSVC.spec] Collecting data files...")

# Collect transformers data files (models, configs, tokenizers)
_transformers_data = []
try:
    _transformers_data = collect_data_files('transformers')
    if _transformers_data:
        print(f"[SoVitsSVC.spec] Collected transformers data files: {len(_transformers_data)} files")
except Exception as e:
    print(f"[SoVitsSVC.spec] WARNING: collect_data_files('transformers') failed: {e}")

# Collect librosa data files (needed for audio processing)
_librosa_data = []
try:
    _librosa_data = collect_data_files('librosa')
    if _librosa_data:
        print(f"[SoVitsSVC.spec] Collected librosa data files: {len(_librosa_data)} files")
except Exception as e:
    print(f"[SoVitsSVC.spec] WARNING: collect_data_files('librosa') failed: {e}")

# Collect soundfile data files
_soundfile_data = []
try:
    _soundfile_data = collect_data_files('soundfile')
    if _soundfile_data:
        print(f"[SoVitsSVC.spec] Collected soundfile data files: {len(_soundfile_data)} files")
except Exception as e:
    print(f"[SoVitsSVC.spec] WARNING: collect_data_files('soundfile') failed: {e}")

# Collect gradio data files (UI templates, assets)
_gradio_data = []
try:
    _gradio_data = collect_data_files('gradio')
    if _gradio_data:
        print(f"[SoVitsSVC.spec] Collected gradio data files: {len(_gradio_data)} files")
except Exception as e:
    print(f"[SoVitsSVC.spec] WARNING: collect_data_files('gradio') failed: {e}")

# Collect gradio_client data files
_gradio_client_data = []
try:
    _gradio_client_data = collect_data_files('gradio_client')
    if _gradio_client_data:
        print(f"[SoVitsSVC.spec] Collected gradio_client data files: {len(_gradio_client_data)} files")
except Exception as e:
    print(f"[SoVitsSVC.spec] WARNING: collect_data_files('gradio_client') failed: {e}")

# Collect dynamic libraries
_soundfile_binaries = []
try:
    _soundfile_binaries = collect_dynamic_libs('soundfile')
    if _soundfile_binaries:
        print(f"[SoVitsSVC.spec] Collected soundfile binaries: {len(_soundfile_binaries)} files")
except Exception as e:
    print(f"[SoVitsSVC.spec] WARNING: collect_dynamic_libs('soundfile') failed: {e}")

a = Analysis(
    ['sovits_app.py'],
    pathex=[],
    binaries=_soundfile_binaries + [
        # Additional binaries can be added here if needed
    ],
    datas=[
        # Include config files
        (str(configs_dir), 'configs'),
        # Include all Python modules from the project
        ('app.py', '.'),
        ('svc_*.py', '.'),
        ('verify_device.py', '.'),
        # Include model directories
        ('models', 'models'),
        ('vits', 'vits'),
        ('vits_decoder', 'vits_decoder'),
        ('vits_extend', 'vits_extend'),
        ('pitch', 'pitch'),
        ('hubert', 'hubert'),
        ('contentvec', 'contentvec'),
        ('whisper', 'whisper'),
        ('data2vec', 'data2vec'),
        ('crepe', 'crepe'),
        ('rmvpe', 'rmvpe'),
        ('speaker', 'speaker'),
        ('utils', 'utils'),
        ('prepare', 'prepare'),
        ('vad', 'vad'),
        ('feature_retrieval', 'feature_retrieval'),
        ('vits_pretrain', 'vits_pretrain'),
        ('hubert_pretrain', 'hubert_pretrain'),
        ('whisper_pretrain', 'whisper_pretrain'),
        ('speaker_pretrain', 'speaker_pretrain'),
    ] + _transformers_data + _librosa_data + _soundfile_data + _gradio_data + _gradio_client_data,
    hiddenimports=[
        # Core imports
        'gradio',
        'gradio.blocks',
        'gradio.components',
        'gradio.processing_utils',
        'gradio_client',
        'gradio_client.utils',
        # Collect all gradio submodules
        *collect_submodules('gradio'),
        *collect_submodules('gradio_client'),
        # PyTorch and related
        'torch',
        'torchaudio',
        'torchvision',
        # Collect all transformers submodules
        *collect_submodules('transformers'),
        # Audio processing
        'librosa',
        'soundfile',
        'scipy',
        'scipy.signal',
        'resampy',
        'audiomentations',
        # ML/Scientific
        'numpy',
        'sklearn',
        'scikit-learn',
        'faiss',
        'omegaconf',
        # Other dependencies
        'yaml',
        'ruamel.yaml',
        'matplotlib',
        'tensorboard',
        'tqdm',
        'fsspec',
        'pyworld',
        'chardet',
        # pywebview for native window
        'webview',
        'webview.platforms.cocoa',
        # Standard library modules that might be missed
        'queue',
        'threading',
        'socket',
        'webbrowser',
        'locale',
        'shlex',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test and development packages
        'pytest',
        'setuptools',
        'pip',
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
    [],
    exclude_binaries=True,
    name='SoVitsSVC_bin',  # Will be renamed to SoVitsSVC in the app bundle
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Hide console window - pywebview provides native UI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SoVitsSVC',
)

# macOS app bundle
app = BUNDLE(
    coll,
    name='SoVitsSVC.app',
    icon=str(icon_path) if icon_path.exists() else None,
    bundle_identifier='com.sovitssvc.app',
    info_plist={
        'CFBundleName': 'SoVitsSVC',
        'CFBundleDisplayName': 'SoVits-SVC 5.0',
        'CFBundleShortVersionString': '5.0.0',
        'CFBundleVersion': '5.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '12.0',
        'NSRequiresAquaSystemAppearance': False,
        # Show in dock and run in foreground (native app experience)
        'LSUIElement': False,
        'LSBackgroundOnly': False,
        'CFBundlePackageType': 'APPL',
        # Permissions
        'NSMicrophoneUsageDescription': 'SoVits-SVC needs access to your microphone for voice recording and conversion.',
        'NSCameraUsageDescription': 'SoVits-SVC may need camera access for future features.',
        # Network access
        'NSAppTransportSecurity': {
            'NSAllowsLocalNetworking': True,
        },
        # CFBundleExecutable: will be set to SoVitsSVC after copying SoVitsSVC_bin
        'CFBundleExecutable': 'SoVitsSVC',
    },
)
