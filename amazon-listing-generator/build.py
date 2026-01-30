"""
构建脚本 - 将Python应用打包为EXE文件
"""

import PyInstaller.__main__
import os
import shutil
import sys


def build_exe():
    """
    使用PyInstaller构建EXE文件
    """
    # 确保输出目录存在
    dist_dir = os.path.join(os.getcwd(), 'dist')
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    # PyInstaller参数
    args = [
        'src/main.py',                    # 主程序入口
        '--name=AmazonListingGenerator',  # 生成的EXE文件名
        '--windowed',                     # 创建窗口化应用（无控制台）
        '--onedir',                       # 创建单个目录（而不是单文件）
        '--add-data=src/image_processor.py;src',  # 添加模块
        '--add-data=src/amazon_api.py;src',       # 添加模块
        '--add-data=src/llm_processor.py;src',    # 添加模块
        '--hidden-import=requests',       # 隐式导入
        '--hidden-import=bs4',            # 隐式导入
        '--hidden-import=lxml',           # 隐式导入
        '--hidden-import=PIL',            # 隐式导入
        '--hidden-import=transformers',   # 隐式导入
        '--hidden-import=torch',          # 隐式导入
        '--collect-all=PIL',              # 收集PIL所有文件
        '--collect-all=transformers',     # 收集transformers所有文件
        '--collect-all=torch',            # 收集torch所有文件
        '--clean',                        # 清理临时文件
        '--noconfirm',                    # 不要求确认
    ]
    
    print("开始构建EXE文件...")
    print(f"构建参数: {' '.join(args)}")
    
    try:
        PyInstaller.__main__.run(args)
        print("EXE文件构建成功!")
        
        # 检查生成的文件
        exe_path = os.path.join(dist_dir, 'AmazonListingGenerator')
        if os.path.exists(exe_path):
            print(f"EXE文件位置: {exe_path}")
            print("构建完成！您可以在dist/AmazonListingGenerator/目录下找到可执行文件。")
        else:
            print("警告: 未找到预期的EXE文件")
            
    except Exception as e:
        print(f"构建过程中出现错误: {e}")
        sys.exit(1)


def install_dependencies():
    """
    安装构建所需的依赖
    """
    import subprocess
    
    print("安装构建依赖...")
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', 'pyinstaller', 'cx_Freeze'
    ])
    
    # 安装项目依赖
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
    ])


if __name__ == "__main__":
    print("Amazon Listing Generator - 构建工具")
    print("="*50)
    
    # 安装依赖
    install_dependencies()
    
    # 构建EXE
    build_exe()