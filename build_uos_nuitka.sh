#!/bin/bash
# 配网通 - 统信UOS Nuitka编译脚本（代码保护版）
# Nuitka会将Python编译为C代码再编译为机器码，几乎无法反编译

echo "=========================================="
echo "  配网通 V1.0 - Nuitka编译（代码保护）"
echo "=========================================="

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3"
    exit 1
fi

# 检查gcc
if ! command -v gcc &> /dev/null; then
    echo "[错误] 未找到gcc编译器，请先安装: sudo apt install gcc python3-dev"
    exit 1
fi

echo "[1/4] 安装Nuitka..."
pip3 install nuitka

echo "[2/4] 安装Python依赖..."
pip3 install -r requirements.txt

echo "[3/4] 安装Tkinter..."
sudo apt-get install -y python3-tk 2>/dev/null || echo "Tkinter已安装"

echo "[4/4] 开始编译（可能需要几分钟）..."
python3 -m nuitka \
    --standalone \
    --onefile \
    --output-filename=配网通 \
    --include-package=paramiko \
    --include-package=requests \
    --include-package=psutil \
    --include-package=cryptography \
    main.py

echo ""
echo "=========================================="
echo "  编译完成！"
echo "=========================================="
echo ""
echo "可执行文件: dist/配网通.bin"
echo "运行方式: ./dist/配网通.bin"
echo ""
echo "注意：Nuitka编译的是真正的机器码，无法被反编译还原为Python源码"
