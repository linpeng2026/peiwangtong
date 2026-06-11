# 配网通 - 企业级交换路由自动配置系统

<div align="center">

**AI驱动的网络设备智能配置与运维平台**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-green.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20UOS-lightgrey.svg)]()

</div>

---

## 产品概述

**配网通** 是一款面向企业网络工程师的智能化运维工具，深度融合 AI 大模型与网络运维场景，实现从设备配置到网络诊断的全流程自动化。

### 核心价值

- **AI 驱动**：自然语言描述需求，自动生成专业配置命令
- **开箱即用**：支持 Windows 和统信 UOS 双平台
- **全面诊断**：12 种网络运维工具，覆盖日常运维场景
- **安全可控**：代码编译为机器码交付，保护知识产权

---

## 功能模块

### 一、AI 智能配置

| 功能 | 说明 |
|------|------|
| **设备选择** | 支持华为、H3C、锐捷、思科等主流厂商，三级联动（厂商→类型→型号） |
| **AI 生成命令** | 自然语言描述需求，AI 自动生成配置命令，支持 DeepSeek、通义千问、豆包等多种 AI 厂商 |
| **AI 结果分析** | 粘贴设备回显，AI 自动分析配置结果，识别错误和建议 |
| **配置历史** | 自动保存历史命令，支持一键复制 |

### 二、网络计算工具

| 功能 | 说明 |
|------|------|
| **子网计算器** | 输入 IP/CIDR，自动计算网络地址、广播地址、可用主机范围 |
| **VLAN 规划** | 根据需求自动规划 VLAN 分配方案 |
| **IP 地址规划** | 批量 IP 地址分配与冲突检测 |
| **AI 协助** | AI 辅助解决各种网络问题 |

### 三、网络运维工具

| 功能 | 说明 |
|------|------|
| **仪表板** | 实时显示 CPU/内存/网络状态、本机 IP/MAC/外网 IP |
| **网络健康检查** | 一键检测 DNS/网关/外网连通性/延迟 |
| **外网测速** | 测试下载/上传速度，多源备用 |
| **内网测速** | TCP/UDP 内网带宽测试 |
| **路由追踪** | 可视化 Traceroute，支持停止 |
| **端口扫描** | 快速/全面扫描，支持停止 |
| **主机发现** | 三阶段扫描（Ping→SYN→ARP/NBT），自动获取 MAC 和厂商 |
| **摄像头扫描** | 自动发现 ONVIF 摄像头设备 |
| **外网 IP 检测** | 多 API 备选获取外网 IP |
| **DHCP 检测** | 显示所有网络适配器的 DHCP/静态 IP 信息 |
| **MAC 厂商查询** | 内置 39,000+ OUI 记录，精准识别厂商 |
| **网络接口信息** | 显示所有网卡的详细配置信息 |

---

## 技术特点

1. **三阶段主机发现算法**：Ping 快速扫描 → SYN 端口探测 → ARP/NBT 深度识别
2. **智能网段自动识别**：基于 socket 路由表获取真实通信 IP
3. **多 AI 厂商支持**：DeepSeek、通义千问、豆包、自定义 API
4. **MAC OUI 数据库**：内置 39,497 条厂商记录
5. **异步 UI 架构**：多线程 + 批量更新，界面流畅不卡顿
6. **跨平台支持**：Windows + 统信 UOS（Linux）
7. **代码保护**：Nuitka 编译为原生机器码，无法反编译
8. **配置持久化**：AI API 配置自动保存，无需重复输入

---

## 系统要求

### Windows
- Windows 10/11
- 直接运行 `配网通.exe`，无需安装 Python

### 统信 UOS
- 统信 UOS 20+（Debian 10/11）
- Python 3.7+
- GCC 编译器（用于 Nuitka 编译）

---

## 快速开始

### Windows

直接双击 `dist/配网通.exe` 运行。

### 统信 UOS

```bash
# 安装依赖
sudo apt install gcc python3-dev python3-tk
pip3 install -r requirements.txt

# Nuitka 编译（代码保护）
bash build_uos_nuitka.sh

# 运行
./dist/配网通.bin
```

详细部署指南见 [UOS部署指南.md](UOS部署指南.md)

---

## 项目结构

```
配网通/
── main.py              # 主程序入口
── ai_client.py         # AI 客户端（多厂商支持）
├── network_device.py    # 网络设备 SSH 连接
├── network_tools.py     # 网络计算工具
├── ops_tools.py         # 网络运维工具（12个子功能）
├── device_models.py     # 设备型号数据库
├── oui.txt              # MAC 厂商 OUI 数据库（39,497条）
├── requirements.txt     # Python 依赖
├── build_uos.sh         # UOS PyInstaller 打包脚本
├── build_uos_nuitka.sh  # UOS Nuitka 编译脚本
├── create_desktop.sh    # UOS 桌面快捷方式脚本
├── ico.ico              # 程序图标
└── version.txt          # 版本信息
```

---

## 许可证

Copyright (C) 2026 林鹏. All rights reserved.

本项目为商业软件，未经授权不得复制、修改、分发。

---

## 联系方式

- **制作人**：林鹏
- **版本**：V1.0
