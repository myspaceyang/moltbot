#!/bin/bash
# Amazon Listing Generator 构建脚本 - 单文件版本

echo "正在安装PyInstaller..."
pip install pyinstaller

if [ $? -ne 0 ]; then
    echo "安装PyInstaller失败"
    exit 1
fi

echo "正在构建单文件EXE..."
pyinstaller --name=AmazonListingGenerator \
    --windowed \
    --onefile \
    --add-data "src:src" \
    --hidden-import=requests \
    --hidden-import=urllib3 \
    --hidden-import=certifi \
    --hidden-import=idna \
    --hidden-import=chardet \
    --hidden-import=charset_normalizer \
    --hidden-import=bs4 \
    --hidden-import=lxml \
    --hidden-import=soupsieve \
    --hidden-import=PIL \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=PIL._imagingtk \
    --hidden-import=tkinter \
    --hidden-import=tkinter.filedialog \
    --hidden-import=tkinter.messagebox \
    --hidden-import=tkinter.scrolledtext \
    --hidden-import=json \
    --hidden-import=urllib.parse \
    --hidden-import=re \
    --hidden-import=threading \
    --hidden-import=os \
    --hidden-import=time \
    --hidden-import=random \
    --hidden-import=openai \
    --hidden-import=openai.types \
    --hidden-import=openai.resources \
    --hidden-import=python_dotenv \
    --hidden-import=transformers \
    --hidden-import=transformers.pipelines \
    --hidden-import=transformers.models \
    --hidden-import=torch \
    --hidden-import=torch.nn \
    --hidden-import=torch.functional \
    --hidden-import=torch.optim \
    --hidden-import=torch.utils \
    --hidden-import=torch.utils.data \
    --clean \
    src/main.py

if [ $? -ne 0 ]; then
    echo "使用spec文件构建单文件EXE..."
    pyinstaller --onefile spec_file.py
    if [ $? -ne 0 ]; then
        echo "构建失败"
        exit 1
    fi
fi

echo "构建完成！"
echo "单文件EXE位于 dist/ 目录中，文件名为 AmazonListingGenerator.exe"