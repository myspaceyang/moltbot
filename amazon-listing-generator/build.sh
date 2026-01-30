#!/bin/bash
# Amazon Listing Generator 构建脚本

echo "正在安装PyInstaller..."
pip install pyinstaller

if [ $? -ne 0 ]; then
    echo "安装PyInstaller失败"
    exit 1
fi

echo "正在构建EXE文件..."
pyinstaller --name=AmazonListingGenerator \
    --windowed \
    --onedir \
    --add-data "src:src" \
    --hidden-import=requests \
    --hidden-import=bs4 \
    --hidden-import=lxml \
    --hidden-import=PIL \
    --hidden-import=tkinter \
    --collect-all=PIL \
    --clean \
    src/main_simple.py

if [ $? -ne 0 ]; then
    echo "构建失败"
    exit 1
fi

echo "构建完成！"
echo "EXE文件位于 dist/AmazonListingGenerator 目录中"