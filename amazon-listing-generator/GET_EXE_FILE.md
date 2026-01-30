# 获取 AmazonListingGenerator.exe 文件

由于仓库无法存储大型二进制文件（如.exe文件），请按照以下步骤获取可执行文件：

## 方法一：使用构建脚本（推荐）

1. 克隆此仓库：
```bash
git clone https://github.com/myspaceyang/moltbot.git
cd moltbot/amazon-listing-generator
```

2. 安装构建工具：
```bash
pip install -r build-assets/requirements.txt
```

3. 运行构建脚本：
```bash
# Linux/Mac:
cd build-assets && chmod +x build.sh && ./build.sh

# Windows:
cd build-assets && build.bat
```

4. 构建完成后，EXE文件将在 `dist/AmazonListingGenerator.exe` 位置

## 方法二：从发布页面下载

我们将EXE文件作为发布资产放在GitHub Releases页面。请访问：
https://github.com/myspaceyang/moltbot/releases

下载最新版本的 `AmazonListingGenerator.exe` 文件。

## 方法三：手动构建

如果您想要手动构建，请参考 `build-assets/` 目录中的构建脚本和SPEC文件。