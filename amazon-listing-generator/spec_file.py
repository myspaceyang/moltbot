# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含所有源代码文件
        ('src/*.py', 'src'),
        # 包含可能的配置和资源文件
        ('*.txt', '.'),
        ('*.md', '.'),
    ],
    hiddenimports=[
        'requests',
        'urllib3',
        'certifi',
        'idna',
        'chardet',
        'charset_normalizer',
        'bs4',
        'lxml',
        'soupsieve',
        'PIL',
        'PIL._tkinter_finder',
        'PIL._imagingtk',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'json',
        'urllib',
        'urllib.parse',
        'urllib.request',
        're',
        'threading',
        'os',
        'time',
        'random',
        'openai',
        'openai.types',
        'openai.resources',
        'python_dotenv',
        'transformers',
        'transformers.pipelines',
        'transformers.models',
        'torch',
        'torch.nn',
        'torch.functional',
        'torch.optim',
        'torch.utils',
        'torch.utils.data',
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
    name='AmazonListingGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False以隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
    onefile=True  # 单文件模式
)