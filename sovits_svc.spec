# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for SoVitsSVC (macOS)

import sys
from pathlib import Path

# Import PyInstaller utilities for collecting binaries and data files
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs, collect_all
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

# Explicitly include Gradio frontend assets (templates, static files)
# Using explicit inclusion instead of collect_data_files() for reliability
# This follows the CTFN-Studio pattern of explicit asset inclusion
_gradio_data = []
_gradio_client_data = []
try:
    import gradio
    import gradio_client
    gradio_path = Path(gradio.__file__).parent
    gradio_client_path = Path(gradio_client.__file__).parent
    
    # Explicitly include Gradio's templates directory (contains frontend assets)
    templates_dir = gradio_path / 'templates'
    if templates_dir.exists():
        _gradio_data.append((str(templates_dir), 'gradio/templates'))
        print(f"[SoVitsSVC.spec] Explicitly included gradio/templates directory")
    else:
        raise RuntimeError(f"Gradio templates directory not found at {templates_dir}")
    
    # Also collect other Gradio data files (configs, etc.) but not relying solely on them
    try:
        _gradio_data_extra = collect_data_files('gradio')
        # Filter out templates directory since we're including it explicitly
        # Use path-based check to avoid excluding unrelated files
        templates_path_str = str(templates_dir)
        _gradio_data_extra = [(src, dst) for src, dst in _gradio_data_extra 
                               if not src.startswith(templates_path_str)]
        _gradio_data.extend(_gradio_data_extra)
        print(f"[SoVitsSVC.spec] Collected additional gradio data files: {len(_gradio_data_extra)} files")
    except Exception as e:
        print(f"[SoVitsSVC.spec] WARNING: collect_data_files('gradio') failed: {e}, but templates are explicitly included")
    
    # Collect gradio_client data files
    try:
        _gradio_client_data = collect_data_files('gradio_client')
        print(f"[SoVitsSVC.spec] Collected gradio_client data files: {len(_gradio_client_data)} files")
    except Exception as e:
        print(f"[SoVitsSVC.spec] WARNING: collect_data_files('gradio_client') failed: {e}")
        
    print(f"[SoVitsSVC.spec] Total gradio data entries: {len(_gradio_data)}, gradio_client entries: {len(_gradio_client_data)}")
    
except Exception as e:
    import traceback
    error_details = traceback.format_exc()
    print(f"[SoVitsSVC.spec] CRITICAL ERROR: Failed to collect Gradio assets!")
    print(f"[SoVitsSVC.spec] Error details:\n{error_details}")
    raise RuntimeError(
        f"Failed to include Gradio frontend assets. The app UI will not work.\n"
        f"Error: {e}\n"
        f"This may be due to incompatible gradio/gradio-client versions.\n"
        f"Ensure 'gradio==3.36.1' and 'gradio-client>=0.2.7,<1.0' are installed."
    )

# Collect dynamic libraries
_soundfile_binaries = []
try:
    _soundfile_binaries = collect_dynamic_libs('soundfile')
    if _soundfile_binaries:
        print(f"[SoVitsSVC.spec] Collected soundfile binaries: {len(_soundfile_binaries)} files")
except Exception as e:
    print(f"[SoVitsSVC.spec] WARNING: collect_dynamic_libs('soundfile') failed: {e}")

# Collect yaml (PyYAML) and ruamel.yaml - required by app.py; use collect_all so they are in bundle (PyInstaller paths)
_yaml_datas, _yaml_binaries, _yaml_hidden = [], [], []
_ruamel_datas, _ruamel_binaries, _ruamel_hidden = [], [], []
try:
    _yaml_datas, _yaml_binaries, _yaml_hidden = collect_all('yaml')
except Exception as e:
    print(f"[SoVitsSVC.spec] WARNING: collect_all('yaml') failed: {e}. Install PyYAML for the app to work.")
try:
    _ruamel_datas, _ruamel_binaries, _ruamel_hidden = collect_all('ruamel.yaml')
except Exception as e:
    print(f"[SoVitsSVC.spec] WARNING: collect_all('ruamel.yaml') failed: {e}. Install ruamel.yaml for the app to work.")

a = Analysis(
    ['sovits_app.py'],
    pathex=[],
    binaries=_soundfile_binaries + _yaml_binaries + _ruamel_binaries + [
        # Additional binaries can be added here if needed
    ],
    datas=[
        # Include config files
        (str(configs_dir), 'configs'),
        *_yaml_datas,
        *_ruamel_datas,
        # Include all project Python files as data (they're also in hiddenimports for imports)
        ('app.py', '.'),
        # Include model directories as data (templates, configs, etc.)
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
        # Other dependencies (collect_all above adds yaml/ruamel.yaml into bundle)
        *_yaml_hidden,
        *_ruamel_hidden,
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
