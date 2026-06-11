# 配网通 V1.0 — 统信UOS部署指南

## 系统要求

- **操作系统**：统信 UOS 20+（基于 Debian 10/11）
- **Python**：Python 3.7+
- **依赖**：Tkinter、pip3

---

## 方式一：Nuitka 编译（代码保护，推荐）

> **Nuitka** 会将 Python 代码编译为 C 代码，再编译为原生机器码，**无法被反编译**，适合交付给客户。

### 步骤

1. **将 `配网通_源码及程序.rar` 解压到 UOS 系统中**

2. **打开终端，进入解压目录**
   ```bash
   cd /path/to/配网通
   ```

3. **安装 C 编译器**
   ```bash
   sudo apt install gcc python3-dev
   ```

4. **赋予脚本执行权限**
   ```bash
   chmod +x build_uos_nuitka.sh create_desktop.sh
   ```

5. **运行编译脚本**
   ```bash
   bash build_uos_nuitka.sh
   ```

6. **等待编译完成**（可能需要几分钟），可执行文件位于 `dist/配网通.bin`

7. **运行程序**
   ```bash
   ./dist/配网通.bin
   ```

8. **（可选）创建桌面快捷方式**
   ```bash
   bash create_desktop.sh
   ```

---

## 方式二：PyInstaller 打包（快速，但代码可被提取）

> PyInstaller 只是打包，**可以被反编译提取源码**。适合内部使用或快速测试。

### 步骤

1. **将 `配网通_源码及程序.rar` 解压到 UOS 系统中**

2. **打开终端，进入解压目录**
   ```bash
   cd /path/to/配网通
   ```

3. **赋予脚本执行权限**
   ```bash
   chmod +x build_uos.sh create_desktop.sh
   ```

4. **运行打包脚本**
   ```bash
   bash build_uos.sh
   ```

5. **等待打包完成**，可执行文件位于 `dist/配网通`

6. **运行程序**
   ```bash
   ./dist/配网通
   ```

7. **（可选）创建桌面快捷方式**
   ```bash
   bash create_desktop.sh
   ```

---

## 方式三：直接运行（无需打包）

### 1. 安装依赖

```bash
# 安装 Python3 和 pip
sudo apt update
sudo apt install python3 python3-pip python3-tk

# 安装 Python 依赖
pip3 install -r requirements.txt
```

### 2. 打包

```bash
pyinstaller --onefile --windowed \
    --name="配网通" \
    --hidden-import=paramiko \
    --hidden-import=cryptography \
    --hidden-import=bcrypt \
    --hidden-import=requests \
    --hidden-import=psutil \
    main.py
```

### 3. 运行

```bash
./dist/配网通
```

---

## 方式三：直接运行（无需打包）

如果不想打包，也可以直接运行 Python 脚本：

```bash
# 安装依赖
pip3 install -r requirements.txt

# 运行
python3 main.py
```

---

## 常见问题

### Q1: 提示找不到 Tkinter
```bash
sudo apt install python3-tk
```

### Q2: pip3 安装依赖失败
```bash
# 使用国内镜像源
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 打包后运行提示缺少库
```bash
# 安装系统级依赖
sudo apt install libssl-dev libffi-dev
```

### Q4: 图标不显示
UOS 可能不支持 `.ico` 格式图标，可转换为 `.png`：
```bash
# 安装 imagemagick
sudo apt install imagemagick
convert ico.ico 配网通.png
```
然后修改 `create_desktop.sh` 中的图标路径。

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `build_uos.sh` | UOS 一键打包脚本 |
| `create_desktop.sh` | 创建桌面快捷方式脚本 |
| `requirements.txt` | Python 依赖列表 |
| `main.py` | 主程序 |
| `dist/配网通` | 打包后的可执行文件 |

---

**制作人**：林鹏  
**版本**：V1.0  
**Copyright (C) 2026 林鹏. All rights reserved.**
