"""
安装脚本 - 用于创建桌面应用程序安装包
"""

from cx_Freeze import setup, Executable
import sys
import os


# 依赖项
build_options = {
    'packages': [
        'requests', 
        'bs4', 
        'lxml', 
        'PIL', 
        'Pillow', 
        'transformers', 
        'torch',
        'tkinter',
        'json',
        'urllib',
        're',
        'threading',
        'typing',
        'os',
        'time',
        'random'
    ],
    'excludes': [],
    'include_files': [
        # 添加必要的资源文件
    ],
    'optimize': 2
}


# 定义可执行文件
executables = [
    Executable(
        'src/main.py',
        target_name='AmazonListingGenerator.exe',
        base='Win32GUI' if sys.platform == 'win32' else None,  # 无控制台窗口
        icon=None  # 可以添加图标文件路径
    )
]


setup(
    name='Amazon Listing Generator',
    version='1.0.0',
    description='A tool for generating Amazon listings with AI-powered content creation',
    options={'build_exe': build_options},
    executables=executables
)