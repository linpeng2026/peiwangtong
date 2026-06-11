#!/bin/bash
# 配网通 - 统信UOS打包脚本
# 使用方法：在UOS终端中运行 bash build_uos.sh

echo "=========================================="
echo "  配网通 V1.0 - 统信UOS打包脚本"
echo "=========================================="

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[1/4] 安装依赖..."
pip3 install -r requirements.txt

echo "[2/4] 安装Tkinter（如未安装）..."
sudo apt-get install -y python3-tk 2>/dev/null || echo "Tkinter已安装或跳过"

echo "[3/4] 开始打包..."
pyinstaller --onefile --windowed \
    --name="配网通" \
    --hidden-import=paramiko \
    --hidden-import=cryptography \
    --hidden-import=bcrypt \
    --hidden-import=requests \
    --hidden-import=psutil \
    main.py

echo "[4/4] 打包完成！"
echo ""
echo "可执行文件位置: dist/配网通"
echo "运行方式: ./dist/配网通"
echo ""
echo "如需创建桌面快捷方式，可运行: bash create_desktop.sh"
