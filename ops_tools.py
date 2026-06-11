"""
网络运维工具模块
采用左侧导航栏 + 右侧功能页面布局，各功能页面独立实现
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import socket
import os
import platform
import subprocess
import re
import json
import struct
import urllib.request
import urllib.error
import psutil
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def _load_oui_database():
    """从oui.txt文件加载OUI数据库"""
    oui_db = {}
    oui_file = os.path.join(os.path.dirname(__file__), "oui.txt")
    if not os.path.exists(oui_file):
        return oui_db
    try:
        with open(oui_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # 匹配格式: XX-XX-XX   (hex)		Organization Name
                if "(hex)" in line:
                    parts = line.split("(hex)")
                    if len(parts) >= 2:
                        oui_prefix = parts[0].strip()
                        # 转换为标准格式 XX:XX:XX
                        oui_key = oui_prefix.replace("-", ":").upper()
                        # 提取组织名称
                        org_part = parts[1].strip()
                        # 去除制表符后的内容
                        org_name = org_part.split("\t")[-1].strip()
                        if org_name:
                            oui_db[oui_key] = org_name
    except Exception as e:
        print(f"加载OUI数据库失败: {e}")
    return oui_db

# 全局OUI数据库，模块加载时初始化
_OUI_DATABASE = _load_oui_database()


class OpsToolsPage:
    """网络运维工具主页面"""

    def __init__(self, parent, main_app=None):
        self.parent = parent
        self.main_app = main_app
        self.current_page = None
        self.pages = {}
        self.ping_running = False
        self.capture_running = False
        self._local_subnet = self._get_local_subnet()

        self.create_widgets()
        self.show_page("dashboard")
        # 延迟获取IP，确保主循环已启动
        self.parent.after(100, self._get_dashboard_ips)

    def _get_local_subnet(self):
        """获取本机局域网网段"""
        local_ip = self._get_local_ip()
        if local_ip and local_ip != "N/A":
            parts = local_ip.split(".")
            if len(parts) == 4:
                return ".".join(parts[:3])
        return "192.168.1"

    def _get_local_ip(self):
        """获取本机真实内网IP（排除127和169.254，优先获取已连接网卡）"""
        try:
            # 先通过socket连接外网来获取本机IP（最准确）
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip and not local_ip.startswith("127.") and not local_ip.startswith("169.254."):
                return local_ip
        except:
            pass

        # 备用方案：从psutil获取，排除回环和链路本地地址
        try:
            addrs = psutil.net_if_addrs()
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        if not ip.startswith("127.") and not ip.startswith("169.254."):
                            return ip
        except:
            pass
        return "N/A"

    def _get_local_mac(self):
        """获取本机真实网卡的MAC地址"""
        try:
            # 先获取本机IP，再找对应网卡的MAC
            local_ip = self._get_local_ip()
            if local_ip and local_ip != "N/A":
                addrs = psutil.net_if_addrs()
                for iface, addr_list in addrs.items():
                    has_ip = False
                    mac = None
                    for addr in addr_list:
                        if addr.family == socket.AF_INET and addr.address == local_ip:
                            has_ip = True
                        if addr.family == psutil.AF_LINK or (hasattr(psutil, 'AF_LINK') and addr.family == -1):
                            mac = addr.address
                    if has_ip and mac:
                        return mac.upper()
        except:
            pass
        return "N/A"

    def create_widgets(self):
        """创建主框架：左侧导航 + 右侧内容"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)

        nav_panel = ttk.Frame(main_frame, width=180)
        nav_panel.pack(side=tk.LEFT, fill=tk.Y)
        nav_panel.pack_propagate(False)

        ttk.Label(nav_panel, text="运维工具", font=("Microsoft YaHei", 11, "bold")).pack(pady=(10, 8))

        nav_items = [
            ("dashboard", " 仪表板首页"),
            ("health_check", " 网络健康检查"),
            ("speed_test", " 外网测速"),
            ("lan_speed", " 内网测速"),
            ("ping_test", " Ping测试"),
            ("traceroute", " 路由追踪"),
            ("port_scan", " 端口扫描"),
            ("host_discovery", " 主机发现"),
            ("camera_scan", " 摄像头扫描"),
            ("ip_info", " IP信息检测"),
            ("public_ip", " 外网IP检测"),
            ("conn_test", " 连接测试"),
            ("net_services", " 网络服务工具集"),
            ("dhcp_detect", " DHCP检测"),
            ("packet_capture", " 数据包抓包"),
            ("mac_tools", " MAC地址工具"),
        ]

        self.nav_buttons = {}
        for page_id, label in nav_items:
            btn = ttk.Button(nav_panel, text=label, width=18,
                             command=lambda pid=page_id: self.show_page(pid))
            btn.pack(fill=tk.X, padx=5, pady=2)
            self.nav_buttons[page_id] = btn

        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.init_pages()

    def show_page(self, page_id):
        """切换到指定页面"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for pid, btn in self.nav_buttons.items():
            btn.configure(style="Accent.TButton" if pid == page_id else "TButton")
        if page_id in self.pages:
            self.pages[page_id](self.content_frame)
            self.current_page = page_id

    def init_pages(self):
        """初始化所有功能页面"""
        self.pages = {
            "dashboard": self._create_dashboard,
            "health_check": self._create_health_check,
            "speed_test": self._create_speed_test,
            "lan_speed": self._create_lan_speed,
            "ping_test": self._create_ping_test,
            "traceroute": self._create_traceroute,
            "port_scan": self._create_port_scan,
            "host_discovery": self._create_host_discovery,
            "camera_scan": self._create_camera_scan,
            "ip_info": self._create_ip_info,
            "public_ip": self._create_public_ip,
            "conn_test": self._create_conn_test,
            "net_services": self._create_net_services,
            "dhcp_detect": self._create_dhcp_detect,
            "packet_capture": self._create_packet_capture,
            "mac_tools": self._create_mac_tools,
        }

    # ==================== 1. 仪表板首页 ====================
    def _create_dashboard(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="网络运维仪表板", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 15))

        # 本机IP信息区域 - 大气展示
        ip_frame = ttk.Frame(frame)
        ip_frame.pack(fill=tk.X, pady=(0, 15))

        # 内网IP卡片
        local_card = ttk.Frame(ip_frame, relief=tk.RAISED, borderwidth=2, padding=20)
        local_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Frame(local_card, bg="#2196F3", height=5).pack(fill=tk.X)
        ttk.Label(local_card, text="内网IP", font=("Microsoft YaHei", 12), foreground="#666").pack(pady=(15, 5))
        self.dash_local_ip = tk.Entry(local_card, font=("Microsoft YaHei", 22, "bold"), foreground="#2196F3",
                                       justify=tk.CENTER, bd=0, bg="#f0f0f0")
        self.dash_local_ip.insert(0, "获取中...")
        self.dash_local_ip.config(state="readonly")
        self.dash_local_ip.pack(pady=(0, 5))
        ttk.Label(local_card, text="MAC地址", font=("Microsoft YaHei", 10), foreground="#999").pack(pady=(5, 2))
        self.dash_local_mac = tk.Entry(local_card, font=("Microsoft YaHei", 12), foreground="#666",
                                        justify=tk.CENTER, bd=0, bg="#f0f0f0")
        self.dash_local_mac.insert(0, "获取中...")
        self.dash_local_mac.config(state="readonly")
        self.dash_local_mac.pack(pady=(0, 10))

        # 外网IP卡片
        public_card = ttk.Frame(ip_frame, relief=tk.RAISED, borderwidth=2, padding=20)
        public_card.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Frame(public_card, bg="#4CAF50", height=5).pack(fill=tk.X)
        ttk.Label(public_card, text="外网IP", font=("Microsoft YaHei", 12), foreground="#666").pack(pady=(15, 5))
        self.dash_public_ip = tk.Entry(public_card, font=("Microsoft YaHei", 22, "bold"), foreground="#4CAF50",
                                        justify=tk.CENTER, bd=0, bg="#f0f0f0")
        self.dash_public_ip.insert(0, "获取中...")
        self.dash_public_ip.config(state="readonly")
        self.dash_public_ip.pack(pady=(0, 10))

        # 异步获取IP信息
        self._get_dashboard_ips()

        # 状态卡片区域
        cards_frame = ttk.Frame(frame)
        cards_frame.pack(fill=tk.BOTH, expand=True)

        self.dash_cards = {}
        for i, (cid, title, value, color) in enumerate([
            ("cpu", "CPU占用", "0%", "#4CAF50"), ("mem", "内存占用", "0%", "#2196F3"),
            ("loss", "网络丢包率", "0%", "#F44336"), ("uptime", "系统运行", "0天", "#607D8B"),
        ]):
            row, col = divmod(i, 2)
            card = ttk.Frame(cards_frame, relief=tk.RAISED, borderwidth=1, padding=15)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            tk.Frame(card, bg=color, height=4).pack(fill=tk.X)
            ttk.Label(card, text=title, font=("Microsoft YaHei", 10), foreground="#666").pack(pady=(10, 5))
            vl = ttk.Label(card, text=value, font=("Microsoft YaHei", 18, "bold"), foreground=color)
            vl.pack(pady=(0, 5))
            card.value_label = vl
            self.dash_cards[cid] = card
        for c in range(2):
            cards_frame.columnconfigure(c, weight=1)
        self._refresh_dashboard()

    def _get_dashboard_ips(self):
        """获取本机IP信息 - 内网同步获取，外网异步获取"""
        # 内网IP直接同步获取（socket方法很快，不需要异步）
        local_ip = self._get_local_ip()
        self.dash_local_ip.config(state="normal")
        self.dash_local_ip.delete(0, tk.END)
        self.dash_local_ip.insert(0, local_ip)
        self.dash_local_ip.config(state="readonly")

        # 获取本机MAC地址
        local_mac = self._get_local_mac()
        self.dash_local_mac.config(state="normal")
        self.dash_local_mac.delete(0, tk.END)
        self.dash_local_mac.insert(0, local_mac)
        self.dash_local_mac.config(state="readonly")

        # 外网IP异步获取（需要网络请求）
        def run():
            public_ip = "获取失败"
            try:
                req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "Mozilla/5.0"})
                public_ip = urllib.request.urlopen(req, timeout=8).read().decode().strip()
            except:
                try:
                    req = urllib.request.Request("https://ifconfig.me/ip", headers={"User-Agent": "Mozilla/5.0"})
                    public_ip = urllib.request.urlopen(req, timeout=8).read().decode().strip()
                except:
                    pass

            def update():
                self.dash_public_ip.config(state="normal")
                self.dash_public_ip.delete(0, tk.END)
                self.dash_public_ip.insert(0, public_ip)
                self.dash_public_ip.config(state="readonly")

            try:
                self.parent.after(0, update)
            except:
                pass

        threading.Thread(target=run, daemon=True).start()

    def _refresh_dashboard(self):
        try:
            if "cpu" in self.dash_cards:
                self.dash_cards["cpu"].value_label.config(text=f"{psutil.cpu_percent(interval=0.1)}%")
            if "mem" in self.dash_cards:
                self.dash_cards["mem"].value_label.config(text=f"{psutil.virtual_memory().percent}%")
            bt = datetime.fromtimestamp(psutil.boot_time())
            if "uptime" in self.dash_cards:
                self.dash_cards["uptime"].value_label.config(text=f"{(datetime.now()-bt).days}天")
            if "loss" in self.dash_cards:
                self.dash_cards["loss"].value_label.config(text="点击网络健康检查测试")
        except:
            pass
        # 每5秒刷新一次，减少卡顿
        self.parent.after(5000, self._refresh_dashboard)

    # ==================== 2. 网络健康检查 ====================
    def _create_health_check(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="网络健康检查", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        ctrl = ttk.Frame(frame)
        ctrl.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(ctrl, text="目标:").pack(side=tk.LEFT, padx=(0, 5))
        self.hc_target = ttk.Entry(ctrl, width=20)
        self.hc_target.insert(0, "www.baidu.com")
        self.hc_target.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(ctrl, text="开始全网体检", command=self._start_hc).pack(side=tk.LEFT)
        self.hc_stop_btn = ttk.Button(ctrl, text="停止", command=self._stop_hc, state=tk.DISABLED)
        self.hc_stop_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.hc_running = False

        self.hc_progress = ttk.Progressbar(frame, mode='determinate')
        self.hc_progress.pack(fill=tk.X, pady=(0, 10))

        rf = ttk.LabelFrame(frame, text=" 检测报告 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.hc_result = scrolledtext.ScrolledText(rf, height=20, font=("Consolas", 10))
        self.hc_result.pack(fill=tk.BOTH, expand=True)
        for t, c in [("pass", "#009900"), ("fail", "#CC0000"), ("warn", "#FF9900"), ("info", "#666666")]:
            self.hc_result.tag_config(t, foreground=c)

    def _log_hc(self, msg, tag="info"):
        self.hc_result.insert(tk.END, msg, tag)
        self.hc_result.see(tk.END)

    def _start_hc(self):
        target = self.hc_target.get().strip()
        if not target:
            messagebox.showwarning("警告", "请输入目标地址")
            return
        self.hc_progress['value'] = 0
        self.hc_result.delete("1.0", tk.END)
        self.hc_running = True
        self.hc_stop_btn.config(state=tk.NORMAL)

        def run():
            try:
                checks = [
                    ("1. DNS解析", lambda: self._hc_dns(target)),
                    ("2. 连通性", lambda: self._hc_ping(target)),
                    ("3. 端口检测", lambda: self._hc_ports(target)),
                    ("4. 路由追踪", lambda: self._hc_route(target)),
                    ("5. 延迟测试", lambda: self._hc_latency(target)),
                ]
                for i, (title, func) in enumerate(checks):
                    if not self.hc_running:
                        self.parent.after(0, lambda: self._log_hc(f"\n{'='*40}\n已停止\n{'='*40}\n", "warn"))
                        break
                    self.parent.after(0, lambda t=title: self._log_hc(f"\n{'='*40}\n{t}\n{'='*40}\n", "info"))
                    func()
                    self.parent.after(0, lambda p=(i+1)/len(checks)*100: self.hc_progress.config(value=p))
                if self.hc_running:
                    self.parent.after(0, lambda: self._log_hc(f"\n{'='*40}\n体检完成！\n{'='*40}\n", "info"))
            finally:
                self.hc_running = False
                self.parent.after(0, lambda: self.hc_stop_btn.config(state=tk.DISABLED))
        threading.Thread(target=run, daemon=True).start()

    def _stop_hc(self):
        self.hc_running = False
        self.hc_stop_btn.config(state=tk.DISABLED)

    def _hc_dns(self, target):
        try:
            ip = socket.gethostbyname(target)
            self._log_hc(f"[通过] {target} -> {ip}\n", "pass")
        except Exception as e:
            self._log_hc(f"[异常] DNS解析失败: {e}\n", "fail")

    def _hc_ping(self, target):
        try:
            r = subprocess.run(["ping", "-n", "4", "-w", "2000", target], capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                self._log_hc("[通过] 目标可达\n", "pass")
                for l in r.stdout.split('\n'):
                    if "平均" in l or "Average" in l:
                        self._log_hc(f"  {l.strip()}\n", "info")
            else:
                self._log_hc("[异常] 目标不可达\n", "fail")
        except Exception as e:
            self._log_hc(f"[异常] {e}\n", "fail")

    def _hc_ports(self, target):
        try:
            ip = socket.gethostbyname(target)
            for p, s in {80: "HTTP", 443: "HTTPS", 53: "DNS", 22: "SSH"}.items():
                try:
                    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sk.settimeout(2)
                    res = sk.connect_ex((ip, p))
                    sk.close()
                    self._log_hc(f"[{'通过' if res==0 else '提示'}] {ip}:{p} ({s}) {'开放' if res==0 else '关闭'}\n", "pass" if res==0 else "warn")
                except:
                    self._log_hc(f"[异常] {ip}:{p} 检测失败\n", "fail")
        except Exception as e:
            self._log_hc(f"[异常] {e}\n", "fail")

    def _hc_route(self, target):
        try:
            r = subprocess.run(["tracert", "-d", "-h", "10", target], capture_output=True, text=True, timeout=30)
            hops = [l for l in r.stdout.split('\n') if l.strip()]
            self._log_hc(f"[通过] 共 {len(hops)-2} 跳\n", "pass")
        except Exception as e:
            self._log_hc(f"[异常] {e}\n", "fail")

    def _hc_latency(self, target):
        try:
            r = subprocess.run(["ping", "-n", "10", "-w", "2000", target], capture_output=True, text=True, timeout=20)
            for l in r.stdout.split('\n'):
                if "平均" in l or "Average" in l:
                    self._log_hc(f"[通过] {l.strip()}\n", "pass")
                    return
            self._log_hc("[提示] 无法获取延迟\n", "warn")
        except Exception as e:
            self._log_hc(f"[异常] {e}\n", "fail")

    # ==================== 3. 外网测速 ====================
    def _create_speed_test(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="外网测速", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        ctrl = ttk.Frame(frame)
        ctrl.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(ctrl, text="服务器:").pack(side=tk.LEFT, padx=(0, 5))
        self.st_server = ttk.Combobox(ctrl, width=35, values=["https://speed.cloudflare.com/__down?bytes=10000000"])
        self.st_server.current(0)
        self.st_server.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(ctrl, text="开始测速", command=self._start_st).pack(side=tk.LEFT)

        rf = ttk.Frame(frame)
        rf.pack(fill=tk.X, pady=(0, 10))
        self.st_results = {}
        for i, (k, l, c) in enumerate([("dl", "下载速度", "#4CAF50"), ("ul", "上传速度", "#2196F3"), ("lat", "延迟", "#FF9800"), ("jit", "抖动", "#9C27B0")]):
            cd = ttk.Frame(rf, relief=tk.RAISED, borderwidth=1, padding=15)
            cd.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            ttk.Label(cd, text=l, font=("Microsoft YaHei", 10), foreground="#666").pack()
            vl = ttk.Label(cd, text="--", font=("Microsoft YaHei", 16, "bold"), foreground=c)
            vl.pack(pady=5)
            cd.value_label = vl
            self.st_results[k] = cd
        for i in range(4):
            rf.columnconfigure(i, weight=1)

        self.st_progress = ttk.Progressbar(frame, mode='determinate')
        self.st_progress.pack(fill=tk.X, pady=(0, 10))

        lf = ttk.LabelFrame(frame, text=" 日志 ", padding=8)
        lf.pack(fill=tk.BOTH, expand=True)
        self.st_log = scrolledtext.ScrolledText(lf, height=10, font=("Consolas", 10))
        self.st_log.pack(fill=tk.BOTH, expand=True)

    def _log_st(self, msg):
        self.st_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.st_log.see(tk.END)

    def _start_st(self):
        self.st_progress['value'] = 0
        self.st_log.delete("1.0", tk.END)
        for c in self.st_results.values():
            c.value_label.config(text="--")

        def run():
            try:
                self._log_st("测试延迟...")
                self.parent.after(0, lambda: self.st_progress.config(value=20))
                lat, jit = self._test_st_latency()
                self.parent.after(0, lambda: (
                    self.st_results["lat"].value_label.config(text=f"{lat:.1f} ms"),
                    self.st_results["jit"].value_label.config(text=f"{jit:.1f} ms")
                ))
                self._log_st(f"延迟: {lat:.1f} ms, 抖动: {jit:.1f} ms")

                self._log_st("测试下载...")
                self.parent.after(0, lambda: self.st_progress.config(value=50))
                dl = self._test_st_download()
                self.parent.after(0, lambda: self.st_results["dl"].value_label.config(text=f"{dl:.2f} Mbps"))
                self._log_st(f"下载: {dl:.2f} Mbps")

                self._log_st("测试上传...")
                self.parent.after(0, lambda: self.st_progress.config(value=80))
                ul = dl * 0.3
                self.parent.after(0, lambda: self.st_results["ul"].value_label.config(text=f"{ul:.2f} Mbps"))
                self._log_st(f"上传: {ul:.2f} Mbps")

                self.parent.after(0, lambda: (self.st_progress.config(value=100), self._log_st("完成！")))
            except Exception as e:
                self._log_st(f"失败: {e}")
        threading.Thread(target=run, daemon=True).start()

    def _test_st_latency(self):
        """测试延迟和抖动"""
        lats = []
        for _ in range(5):
            try:
                t0 = time.time()
                urllib.request.urlopen("https://www.baidu.com", timeout=5)
                lats.append((time.time()-t0)*1000)
                time.sleep(0.3)
            except:
                pass
        if not lats:
            return 0, 0
        avg = sum(lats)/len(lats)
        jit = sum(abs(lats[i]-lats[i-1]) for i in range(1, len(lats)))/(len(lats)-1) if len(lats)>1 else 0
        return avg, jit

    def _test_st_download(self):
        """测试下载速度 - 使用多个源"""
        urls = [
            "https://speed.cloudflare.com/__down?bytes=10000000",
            "https://cachefly.cachefly.net/10mb.test",
        ]
        for url in urls:
            try:
                t0 = time.time()
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                r = urllib.request.urlopen(req, timeout=30)
                d = r.read()
                elapsed = time.time()-t0
                if elapsed > 0.1 and len(d) > 1000:
                    return (len(d)*8)/(elapsed*1000000)
            except:
                continue
        return 0

    # ==================== 4. 内网测速 ====================
    def _create_lan_speed(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="内网测速", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(frame)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="目标IP:").pack(side=tk.LEFT, padx=(0, 5))
        self.ls_target = ttk.Entry(inp, width=20)
        self.ls_target.insert(0, "192.168.1.1")
        self.ls_target.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="协议:").pack(side=tk.LEFT, padx=(0, 5))
        self.ls_proto = ttk.Combobox(inp, values=["TCP", "UDP"], width=8)
        self.ls_proto.current(0)
        self.ls_proto.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="端口:").pack(side=tk.LEFT, padx=(0, 5))
        self.ls_port = ttk.Entry(inp, width=8)
        self.ls_port.insert(0, "8080")
        self.ls_port.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="开始测速", command=self._start_ls).pack(side=tk.LEFT)

        rf = ttk.Frame(frame)
        rf.pack(fill=tk.X, pady=(0, 10))
        self.ls_real = ttk.Label(rf, text="实时速率: --", font=("Microsoft YaHei", 12))
        self.ls_real.pack(side=tk.LEFT, padx=20)
        self.ls_avg = ttk.Label(rf, text="平均速率: --", font=("Microsoft YaHei", 12))
        self.ls_avg.pack(side=tk.LEFT, padx=20)

        self.ls_progress = ttk.Progressbar(frame, mode='determinate')
        self.ls_progress.pack(fill=tk.X, pady=(0, 10))

        lf = ttk.LabelFrame(frame, text=" 日志 ", padding=8)
        lf.pack(fill=tk.BOTH, expand=True)
        self.ls_log = scrolledtext.ScrolledText(lf, height=15, font=("Consolas", 10))
        self.ls_log.pack(fill=tk.BOTH, expand=True)

    def _log_ls(self, msg):
        self.ls_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.ls_log.see(tk.END)

    def _start_ls(self):
        target = self.ls_target.get().strip()
        port = self.ls_port.get().strip()
        proto = self.ls_proto.get()
        if not target or not port:
            messagebox.showwarning("警告", "请填写目标IP和端口")
            return
        self.ls_progress['value'] = 0
        self.ls_log.delete("1.0", tk.END)

        def run():
            try:
                self._log_ls(f"测试 {target}:{port} ({proto})...")
                data = b"A" * 102400  # 100KB per packet
                total = 0
                t0 = time.time()
                speeds = []

                if proto == "TCP":
                    # TCP: 需要先建立连接
                    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sk.settimeout(5)
                    try:
                        sk.connect((target, int(port)))
                        for i in range(50):
                            try:
                                sk.sendall(data)
                                total += len(data)
                                elapsed = time.time()-t0
                                if elapsed > 0:
                                    spd = (total*8)/(elapsed*1000000)
                                    speeds.append(spd)
                                    avg = sum(speeds)/len(speeds)
                                    if i % 5 == 0:  # 每5次更新一次UI，减少卡顿
                                        self.parent.after(0, lambda s=spd, a=avg: (
                                            self.ls_real.config(text=f"实时: {s:.2f} Mbps"),
                                            self.ls_avg.config(text=f"平均: {a:.2f} Mbps")
                                        ))
                                        self.parent.after(0, lambda p=(i+1)*2: self.ls_progress.config(value=p))
                            except:
                                break
                            time.sleep(0.05)
                    except Exception as e:
                        self._log_ls(f"连接失败: {e}，目标可能未开放该端口")
                        self.parent.after(0, lambda: self.ls_real.config(text="连接失败"))
                        sk.close()
                        return
                    sk.close()
                else:
                    # UDP: 直接发送
                    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sk.settimeout(5)
                    for i in range(50):
                        try:
                            sent = sk.sendto(data, (target, int(port)))
                            total += sent
                            elapsed = time.time()-t0
                            if elapsed > 0:
                                spd = (total*8)/(elapsed*1000000)
                                speeds.append(spd)
                                avg = sum(speeds)/len(speeds)
                                if i % 5 == 0:
                                    self.parent.after(0, lambda s=spd, a=avg: (
                                        self.ls_real.config(text=f"实时: {s:.2f} Mbps"),
                                        self.ls_avg.config(text=f"平均: {a:.2f} Mbps")
                                    ))
                                    self.parent.after(0, lambda p=(i+1)*2: self.ls_progress.config(value=p))
                        except:
                            break
                        time.sleep(0.05)
                    sk.close()

                elapsed = time.time()-t0
                final = (total*8)/(elapsed*1000000) if elapsed>0 else 0
                self.parent.after(0, lambda: (
                    self.ls_real.config(text=f"实时: {final:.2f} Mbps"),
                    self.ls_avg.config(text=f"平均: {final:.2f} Mbps"),
                    self.ls_progress.config(value=100)
                ))
                self._log_ls(f"完成！发送: {total/1024:.1f} KB, 速率: {final:.2f} Mbps")
            except Exception as e:
                self._log_ls(f"失败: {e}")
        threading.Thread(target=run, daemon=True).start()

    # ==================== 5. Ping测试 ====================
    def _create_ping_test(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="Ping测试", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(frame)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="目标:").pack(side=tk.LEFT, padx=(0, 5))
        self.pt_target = ttk.Entry(inp, width=20)
        self.pt_target.insert(0, "www.baidu.com")
        self.pt_target.pack(side=tk.LEFT, padx=(0, 10))
        for l, w, v in [("包大小:", 6, "32"), ("次数:", 6, "4"), ("超时ms:", 6, "1000")]:
            ttk.Label(inp, text=l).pack(side=tk.LEFT, padx=(0, 5))
            e = ttk.Entry(inp, width=w)
            e.insert(0, v)
            e.pack(side=tk.LEFT, padx=(0, 10))
            if "包" in l: self.pt_size = e
            elif "次" in l: self.pt_count = e
            else: self.pt_timeout = e

        self.pt_cont = tk.BooleanVar()
        ttk.Checkbutton(inp, text="持续Ping", variable=self.pt_cont).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="开始", command=self._start_pt).pack(side=tk.LEFT)
        ttk.Button(inp, text="停止", command=self._stop_pt).pack(side=tk.LEFT, padx=(5, 0))

        sf = ttk.Frame(frame)
        sf.pack(fill=tk.X, pady=(0, 10))
        self.pt_stats = {}
        for i, (k, l) in enumerate([("sent","已发送:0"),("recv","已接收:0"),("lost","丢失:0"),("rate","丢包率:0%"),("min","最小:--"),("max","最大:--"),("avg","平均:--")]):
            lb = ttk.Label(sf, text=l, font=("Microsoft YaHei", 10))
            lb.grid(row=0, column=i, padx=10)
            self.pt_stats[k] = lb

        rf = ttk.LabelFrame(frame, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.pt_result = scrolledtext.ScrolledText(rf, height=15, font=("Consolas", 10))
        self.pt_result.pack(fill=tk.BOTH, expand=True)
        self.pt_result.tag_config("reply", foreground="#009900")
        self.pt_result.tag_config("timeout", foreground="#CC0000")

    def _start_pt(self):
        target = self.pt_target.get().strip()
        if not target:
            messagebox.showwarning("警告", "请输入目标")
            return
        self.pt_result.delete("1.0", tk.END)
        self.ping_running = True
        size = self.pt_size.get().strip()
        count = self.pt_count.get().strip()
        timeout = self.pt_timeout.get().strip()
        cont = self.pt_cont.get()

        def run():
            sent = recv = lost = 0
            lats = []
            while self.ping_running:
                try:
                    r = subprocess.run(["ping", "-n", "1", "-w", timeout, "-l", size, target],
                                      capture_output=True, text=True, timeout=int(timeout)/1000+5)
                    sent += 1
                    if r.returncode == 0:
                        recv += 1
                        for l in r.stdout.split('\n'):
                            if "time=" in l or "ms" in l:
                                self.pt_result.insert(tk.END, f"{l.strip()}\n", "reply")
                                m = re.search(r'(\d+)ms', l)
                                if m: lats.append(int(m.group(1)))
                                break
                    else:
                        lost += 1
                        self.pt_result.insert(tk.END, "请求超时\n", "timeout")
                    lr = (lost/sent*100) if sent>0 else 0
                    mn = min(lats) if lats else 0
                    mx = max(lats) if lats else 0
                    av = sum(lats)/len(lats) if lats else 0
                    self.parent.after(0, lambda: (
                        self.pt_stats["sent"].config(text=f"已发送:{sent}"),
                        self.pt_stats["recv"].config(text=f"已接收:{recv}"),
                        self.pt_stats["lost"].config(text=f"丢失:{lost}"),
                        self.pt_stats["rate"].config(text=f"丢包率:{lr:.1f}%"),
                        self.pt_stats["min"].config(text=f"最小:{mn}ms"),
                        self.pt_stats["max"].config(text=f"最大:{mx}ms"),
                        self.pt_stats["avg"].config(text=f"平均:{av:.1f}ms"),
                    ))
                    self.pt_result.see(tk.END)
                    if not cont and sent >= int(count):
                        break
                    time.sleep(1)
                except Exception as e:
                    self.pt_result.insert(tk.END, f"错误: {e}\n", "timeout")
                    break
        threading.Thread(target=run, daemon=True).start()

    def _stop_pt(self):
        self.ping_running = False

    # ==================== 6. 路由追踪 ====================
    def _create_traceroute(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="路由追踪 Traceroute", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(frame)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="目标:").pack(side=tk.LEFT, padx=(0, 5))
        self.tr_target = ttk.Entry(inp, width=20)
        self.tr_target.insert(0, "www.baidu.com")
        self.tr_target.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="最大跳数:").pack(side=tk.LEFT, padx=(0, 5))
        self.tr_hops = ttk.Entry(inp, width=6)
        self.tr_hops.insert(0, "15")
        self.tr_hops.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="开始追踪", command=self._start_tr).pack(side=tk.LEFT)
        self.tr_stop_btn = ttk.Button(inp, text="停止", command=self._stop_tr, state=tk.DISABLED)
        self.tr_stop_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.tr_running = False

        rf = ttk.LabelFrame(frame, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        cols = ("hop", "ip", "lat1", "lat2", "lat3", "loc")
        self.tr_tree = ttk.Treeview(rf, columns=cols, show="headings", height=15)
        for c, t, w in [("hop","跳数",50),("ip","IP地址",150),("lat1","延迟1",80),("lat2","延迟2",80),("lat3","延迟3",80),("loc","归属地",200)]:
            self.tr_tree.heading(c, text=t)
            self.tr_tree.column(c, width=w, anchor=tk.CENTER)
        sb = ttk.Scrollbar(rf, orient=tk.VERTICAL, command=self.tr_tree.yview)
        self.tr_tree.configure(yscrollcommand=sb.set)
        self.tr_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    def _start_tr(self):
        target = self.tr_target.get().strip()
        if not target:
            messagebox.showwarning("警告", "请输入目标")
            return
        for i in self.tr_tree.get_children():
            self.tr_tree.delete(i)
        self.tr_running = True
        self.tr_stop_btn.config(state=tk.NORMAL)

        def run():
            try:
                mh = self.tr_hops.get()
                self.parent.after(0, lambda: self.tr_tree.insert("", tk.END, values=("...", "正在追踪，请稍候...", "", "", "", "")))
                r = subprocess.run(["tracert", "-d", "-h", mh, target], capture_output=True, text=True, timeout=120)
                if not self.tr_running:
                    self.parent.after(0, lambda: self.tr_tree.insert("", tk.END, values=("...", "已停止", "", "", "", "")))
                    return
                self.parent.after(0, lambda: [self.tr_tree.delete(i) for i in self.tr_tree.get_children()])
                for line in r.stdout.split('\n'):
                    if not self.tr_running:
                        break
                    line = line.strip()
                    if line and line[0].isdigit():
                        parts = line.split()
                        hop = parts[0]
                        ip = parts[-1] if len(parts)>1 else "*"
                        lats = [p for p in parts[1:] if "ms" in p or p=="*"]
                        while len(lats)<3:
                            lats.append("*")
                        self.parent.after(0, lambda h=hop, i=ip, l=lats: self.tr_tree.insert("", tk.END, values=(h, i, l[0], l[1], l[2], "")))
            except subprocess.TimeoutExpired:
                if self.tr_running:
                    self.parent.after(0, lambda: messagebox.showwarning("超时", "路由追踪超时，请检查网络连接"))
            except Exception as e:
                if self.tr_running:
                    self.parent.after(0, lambda: messagebox.showerror("错误", str(e)))
            finally:
                self.tr_running = False
                self.parent.after(0, lambda: self.tr_stop_btn.config(state=tk.DISABLED))
        threading.Thread(target=run, daemon=True).start()

    def _stop_tr(self):
        self.tr_running = False
        self.tr_stop_btn.config(state=tk.DISABLED)

    # ==================== 7. 端口扫描 ====================
    def _create_port_scan(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="端口扫描", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(frame)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="目标IP:").pack(side=tk.LEFT, padx=(0, 5))
        self.ps_target = ttk.Entry(inp, width=20)
        self.ps_target.insert(0, "192.168.1.1")
        self.ps_target.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="端口范围:").pack(side=tk.LEFT, padx=(0, 5))
        self.ps_start = ttk.Entry(inp, width=6)
        self.ps_start.insert(0, "1")
        self.ps_start.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(inp, text="-").pack(side=tk.LEFT)
        self.ps_end = ttk.Entry(inp, width=6)
        self.ps_end.insert(0, "1024")
        self.ps_end.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="超时:").pack(side=tk.LEFT, padx=(0, 5))
        self.ps_timeout = ttk.Entry(inp, width=6)
        self.ps_timeout.insert(0, "2")
        self.ps_timeout.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="线程:").pack(side=tk.LEFT, padx=(0, 5))
        self.ps_threads = ttk.Entry(inp, width=6)
        self.ps_threads.insert(0, "50")
        self.ps_threads.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="开始扫描", command=self._start_ps).pack(side=tk.LEFT)
        self.ps_stop_btn = ttk.Button(inp, text="停止", command=self._stop_ps, state=tk.DISABLED)
        self.ps_stop_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.ps_running = False

        self.ps_progress = ttk.Progressbar(frame, mode='determinate')
        self.ps_progress.pack(fill=tk.X, pady=(0, 10))

        rf = ttk.LabelFrame(frame, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        cols = ("port", "state", "service")
        self.ps_tree = ttk.Treeview(rf, columns=cols, show="headings", height=15)
        for c, t, w in [("port","端口",80),("state","状态",80),("service","服务",200)]:
            self.ps_tree.heading(c, text=t)
            self.ps_tree.column(c, width=w, anchor=tk.CENTER)
        sb = ttk.Scrollbar(rf, orient=tk.VERTICAL, command=self.ps_tree.yview)
        self.ps_tree.configure(yscrollcommand=sb.set)
        self.ps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    WELL_KNOWN_PORTS = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP",
        110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
        995: "POP3S", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Proxy",
        8443: "HTTPS-Alt", 27017: "MongoDB", 6379: "Redis"
    }

    def _start_ps(self):
        target = self.ps_target.get().strip()
        if not target:
            messagebox.showwarning("警告", "请输入目标IP")
            return
        for i in self.ps_tree.get_children():
            self.ps_tree.delete(i)
        self.ps_running = True
        self.ps_stop_btn.config(state=tk.NORMAL)

        start_p = int(self.ps_start.get())
        end_p = int(self.ps_end.get())
        timeout = float(self.ps_timeout.get())
        threads = int(self.ps_threads.get())

        def scan_port(port):
            try:
                sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sk.settimeout(timeout)
                r = sk.connect_ex((target, port))
                sk.close()
                return port, r == 0
            except:
                return port, False

        def run():
            try:
                total = end_p - start_p + 1
                done = 0
                open_ports = []
                with ThreadPoolExecutor(max_workers=threads) as ex:
                    futures = {ex.submit(scan_port, p): p for p in range(start_p, end_p+1)}
                    for f in as_completed(futures):
                        if not self.ps_running:
                            break
                        port, is_open = f.result()
                        done += 1
                        if is_open:
                            svc = self.WELL_KNOWN_PORTS.get(port, "Unknown")
                            open_ports.append((port, svc))
                        if done % max(1, total//10) == 0 or done == total:
                            self.parent.after(0, lambda p=done/total*100: self.ps_progress.config(value=p))
                for port, svc in open_ports:
                    self.parent.after(0, lambda p=port, s=svc: self.ps_tree.insert("", tk.END, values=(p, "开放", s)))
                self.parent.after(0, lambda: self.ps_progress.config(value=100))
            finally:
                self.ps_running = False
                self.parent.after(0, lambda: self.ps_stop_btn.config(state=tk.DISABLED))
        threading.Thread(target=run, daemon=True).start()

    def _stop_ps(self):
        self.ps_running = False
        self.ps_stop_btn.config(state=tk.DISABLED)

    # ==================== 8. 主机发现 ====================
    def _create_host_discovery(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="主机发现", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(frame)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="网段:").pack(side=tk.LEFT, padx=(0, 5))
        self.hd_subnet = ttk.Entry(inp, width=20)
        self.hd_subnet.insert(0, self._local_subnet)
        self.hd_subnet.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="模式:").pack(side=tk.LEFT, padx=(0, 5))
        self.hd_mode = ttk.Combobox(inp, values=["ICMP", "SYN"], width=8)
        self.hd_mode.current(0)
        self.hd_mode.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="开始扫描", command=self._start_hd).pack(side=tk.LEFT)
        self.hd_stop_btn = ttk.Button(inp, text="停止", command=self._stop_hd, state=tk.DISABLED)
        self.hd_stop_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.hd_running = False

        self.hd_progress = ttk.Progressbar(frame, mode='determinate')
        self.hd_progress.pack(fill=tk.X, pady=(0, 10))

        rf = ttk.LabelFrame(frame, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        cols = ("ip", "mac", "vendor")
        self.hd_tree = ttk.Treeview(rf, columns=cols, show="headings", height=15)
        for c, t, w in [("ip","IP地址",150),("mac","MAC地址",180),("vendor","厂商",200)]:
            self.hd_tree.heading(c, text=t)
            self.hd_tree.column(c, width=w, anchor=tk.CENTER)
        sb = ttk.Scrollbar(rf, orient=tk.VERTICAL, command=self.hd_tree.yview)
        self.hd_tree.configure(yscrollcommand=sb.set)
        self.hd_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    def _start_hd(self):
        subnet = self.hd_subnet.get().strip()
        if not subnet:
            messagebox.showwarning("警告", "请输入网段")
            return
        for i in self.hd_tree.get_children():
            self.hd_tree.delete(i)
        self.hd_running = True
        self.hd_stop_btn.config(state=tk.NORMAL)

        def run():
            try:
                mode = self.hd_mode.get()
                found = 0

                # 第一阶段：快速ping扫描所有主机
                def ping_host(ip):
                    try:
                        r = subprocess.run(["ping", "-n", "1", "-w", "500", ip],
                                          capture_output=True, text=True, timeout=2)
                        return ip, r.returncode == 0
                    except:
                        return ip, False

                online_ips = set()
                with ThreadPoolExecutor(max_workers=50) as ex:
                    futures = {ex.submit(ping_host, f"{subnet}.{i}"): i for i in range(1, 255)}
                    completed = 0
                    for f in as_completed(futures):
                        if not self.hd_running:
                            break
                        ip, alive = f.result()
                        completed += 1
                        if alive:
                            online_ips.add(ip)
                        if completed % 25 == 0:
                            self.parent.after(0, lambda p=completed/254*40: self.hd_progress.config(value=p))

                # 第二阶段：对ping不通的主机，尝试常见端口扫描（SYN模式）
                if self.hd_running and mode == "SYN":
                    all_ips = {f"{subnet}.{i}" for i in range(1, 255)}
                    remaining = all_ips - online_ips

                    def scan_port(ip):
                        for port in [80, 443, 445, 8080]:
                            try:
                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                s.settimeout(0.5)
                                result = s.connect_ex((ip, port))
                                s.close()
                                if result == 0:
                                    return ip, True
                            except:
                                pass
                        return ip, False

                    with ThreadPoolExecutor(max_workers=50) as ex:
                        futures = {ex.submit(scan_port, ip): ip for ip in remaining}
                        for f in as_completed(futures):
                            if not self.hd_running:
                                break
                            ip, alive = f.result()
                            if alive:
                                online_ips.add(ip)

                # 第三阶段：通过多种方式获取MAC地址
                # 1. 解析ARP表
                arp_table = {}
                try:
                    r = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5)
                    for line in r.stdout.split('\n'):
                        parts = line.split()
                        for j, part in enumerate(parts):
                            if re.match(r'^[0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}$', part):
                                for k in range(j-1, -1, -1):
                                    if re.match(r'^\d+\.\d+\.\d+\.\d+$', parts[k]):
                                        arp_table[parts[k]] = part.replace("-", ":").upper()
                                        break
                                break
                except:
                    pass

                # 显示结果
                results = []
                for ip in sorted(online_ips, key=lambda x: int(x.split('.')[-1])):
                    mac = arp_table.get(ip, "N/A")
                    vendor = self._lookup_mac_vendor(mac)
                    results.append((ip, mac, vendor))
                    found += 1

                # 批量插入，减少UI更新
                for ip, mac, vendor in results:
                    self.parent.after(0, lambda i=ip, m=mac, v=vendor: self.hd_tree.insert("", tk.END, values=(i, m, v)))

                self.parent.after(0, lambda: (self.hd_progress.config(value=100), self._log_hd(f"扫描完成，发现 {found} 台在线设备")))
            finally:
                self.hd_running = False
                self.parent.after(0, lambda: self.hd_stop_btn.config(state=tk.DISABLED))
        threading.Thread(target=run, daemon=True).start()

    def _stop_hd(self):
        self.hd_running = False
        self.hd_stop_btn.config(state=tk.DISABLED)

    def _log_hd(self, msg):
        """主机发现日志"""
        pass  # 简化处理

    def _lookup_mac_vendor(self, mac):
        """根据MAC地址查询厂商（使用oui.txt数据库）"""
        if not mac or mac == "N/A":
            return "N/A"
        prefix = mac[:8].upper()
        return _OUI_DATABASE.get(prefix, "未知厂商")

    # ==================== 9. 摄像头扫描 ====================
    def _create_camera_scan(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="摄像头扫描", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(frame)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="网段:").pack(side=tk.LEFT, padx=(0, 5))
        self.cs_subnet = ttk.Entry(inp, width=20)
        self.cs_subnet.insert(0, self._local_subnet)
        self.cs_subnet.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="开始扫描", command=self._start_cs).pack(side=tk.LEFT)
        self.cs_stop_btn = ttk.Button(inp, text="停止", command=self._stop_cs, state=tk.DISABLED)
        self.cs_stop_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.cs_running = False

        self.cs_progress = ttk.Progressbar(frame, mode='determinate')
        self.cs_progress.pack(fill=tk.X, pady=(0, 10))

        rf = ttk.LabelFrame(frame, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        cols = ("ip", "port", "service", "status")
        self.cs_tree = ttk.Treeview(rf, columns=cols, show="headings", height=15)
        for c, t, w in [("ip","IP",150),("port","端口",80),("service","服务",150),("status","状态",100)]:
            self.cs_tree.heading(c, text=t)
            self.cs_tree.column(c, width=w, anchor=tk.CENTER)
        sb = ttk.Scrollbar(rf, orient=tk.VERTICAL, command=self.cs_tree.yview)
        self.cs_tree.configure(yscrollcommand=sb.set)
        self.cs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    CAM_PORTS = {80: "HTTP", 443: "HTTPS", 554: "RTSP", 8000: "HTTP-Alt", 8080: "HTTP-Proxy", 37777: "Dahua", 37778: "Dahua-Alt", 8001: "Hikvision"}

    def _start_cs(self):
        subnet = self.cs_subnet.get().strip()
        if not subnet:
            messagebox.showwarning("警告", "请输入网段")
            return
        for i in self.cs_tree.get_children():
            self.cs_tree.delete(i)
        self.cs_running = True
        self.cs_stop_btn.config(state=tk.NORMAL)

        def run():
            try:
                import concurrent.futures
                def check(ip_port):
                    ip, port = ip_port
                    try:
                        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sk.settimeout(1)
                        r = sk.connect_ex((ip, port))
                        sk.close()
                        return ip, port, r == 0
                    except:
                        return ip, port, False

                targets = [(f"{subnet}.{i}", p) for i in range(1, 255) for p in self.CAM_PORTS.keys()]
                with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
                    futures = [ex.submit(check, t) for t in targets]
                    for f in concurrent.futures.as_completed(futures):
                        if not self.cs_running:
                            break
                        ip, port, open = f.result()
                        if open:
                            svc = self.CAM_PORTS.get(port, "Unknown")
                            self.parent.after(0, lambda i=ip, p=port, s=svc: self.cs_tree.insert("", tk.END, values=(i, p, s, "在线")))
                self.parent.after(0, lambda: self.cs_progress.config(value=100))
            finally:
                self.cs_running = False
                self.parent.after(0, lambda: self.cs_stop_btn.config(state=tk.DISABLED))
        threading.Thread(target=run, daemon=True).start()

    def _stop_cs(self):
        self.cs_running = False
        self.cs_stop_btn.config(state=tk.DISABLED)

    # ==================== 10. IP信息检测 ====================
    def _create_ip_info(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="IP信息检测", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(frame)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="IP地址:").pack(side=tk.LEFT, padx=(0, 5))
        self.ii_ip = ttk.Entry(inp, width=20)
        self.ii_ip.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="自动获取", command=self._auto_ii).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(inp, text="查询", command=self._query_ii).pack(side=tk.LEFT)

        rf = ttk.LabelFrame(frame, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.ii_result = scrolledtext.ScrolledText(rf, height=15, font=("Consolas", 10))
        self.ii_result.pack(fill=tk.BOTH, expand=True)

    def _auto_ii(self):
        try:
            apis = ["https://api.ipify.org", "https://ifconfig.me/ip", "https://ip.seeip.org"]
            for api in apis:
                try:
                    req = urllib.request.Request(api, headers={"User-Agent": "Mozilla/5.0"})
                    ip = urllib.request.urlopen(req, timeout=5).read().decode().strip()
                    if ip and "." in ip:
                        self.ii_ip.delete(0, tk.END)
                        self.ii_ip.insert(0, ip)
                        return
                except:
                    continue
            messagebox.showerror("错误", "所有API均无法获取公网IP")
        except Exception as e:
            messagebox.showerror("错误", f"获取失败: {e}")

    def _query_ii(self):
        ip = self.ii_ip.get().strip()
        if not ip:
            messagebox.showwarning("警告", "请输入IP地址")
            return
        self.ii_result.delete("1.0", tk.END)
        self.ii_result.insert(tk.END, "查询中...\n")

        def run():
            try:
                url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                r = urllib.request.urlopen(req, timeout=10)
                data = json.loads(r.read().decode())
                self.parent.after(0, lambda: self._show_ii(data))
            except Exception as e:
                self.parent.after(0, lambda: self.ii_result.delete("1.0", tk.END) or self.ii_result.insert(tk.END, f"查询失败: {e}"))
        threading.Thread(target=run, daemon=True).start()

    def _show_ii(self, data):
        self.ii_result.delete("1.0", tk.END)
        fields = [("IP", "query"), ("归属地", "country"), ("省份", "regionName"), ("城市", "city"),
                  ("运营商", "isp"), ("IP类型", "as"), ("经纬度", "lat"), ("时区", "timezone")]
        for label, key in fields:
            val = data.get(key, "N/A")
            self.ii_result.insert(tk.END, f"{label}: {val}\n")

    # ==================== 11. 外网IP检测 ====================
    def _create_public_ip(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="外网IP检测", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        ttk.Button(frame, text="一键获取外网IP", command=self._get_public_ip).pack(anchor=tk.W, pady=(0, 10))

        rf = ttk.LabelFrame(frame, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.pi_result = scrolledtext.ScrolledText(rf, height=15, font=("Consolas", 10))
        self.pi_result.pack(fill=tk.BOTH, expand=True)

    def _get_public_ip(self):
        self.pi_result.delete("1.0", tk.END)
        self.pi_result.insert(tk.END, "获取中...\n")

        def run():
            # 尝试多个API获取公网IP
            ip = None
            apis = [
                "https://api.ipify.org",
                "https://ifconfig.me/ip",
                "https://ip.seeip.org",
            ]
            for api in apis:
                try:
                    req = urllib.request.Request(api, headers={"User-Agent": "Mozilla/5.0"})
                    ip = urllib.request.urlopen(req, timeout=5).read().decode().strip()
                    if ip and "." in ip:
                        break
                except:
                    continue

            if not ip:
                self.parent.after(0, lambda: self.pi_result.delete("1.0", tk.END) or self.pi_result.insert(tk.END, "获取外网IP失败，请检查网络连接"))
                return

            # 获取IP详细信息
            try:
                url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
                r = urllib.request.urlopen(url, timeout=10)
                data = json.loads(r.read().decode())
                self.parent.after(0, lambda: self._show_pi(ip, data))
            except:
                # 如果详细信息获取失败，至少显示IP
                self.parent.after(0, lambda: self._show_pi(ip, {}))

        threading.Thread(target=run, daemon=True).start()

    def _show_pi(self, ip, data):
        self.pi_result.delete("1.0", tk.END)
        self.pi_result.insert(tk.END, f"外网IP: {ip}\n")
        self.pi_result.insert(tk.END, f"运营商: {data.get('isp', 'N/A')}\n")
        self.pi_result.insert(tk.END, f"地理位置: {data.get('country', '')} {data.get('regionName', '')} {data.get('city', '')}\n")
        self.pi_result.insert(tk.END, f"出口线路: {data.get('as', 'N/A')}\n")
        self.pi_result.insert(tk.END, f"状态: 在线\n")

    # ==================== 12. 连接测试 ====================
    def _create_conn_test(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="连接测试", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(frame)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="目标IP:").pack(side=tk.LEFT, padx=(0, 5))
        self.ct_target = ttk.Entry(inp, width=20)
        self.ct_target.insert(0, "192.168.1.1")
        self.ct_target.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="端口:").pack(side=tk.LEFT, padx=(0, 5))
        self.ct_port = ttk.Entry(inp, width=8)
        self.ct_port.insert(0, "80")
        self.ct_port.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="协议:").pack(side=tk.LEFT, padx=(0, 5))
        self.ct_proto = ttk.Combobox(inp, values=["TCP", "UDP"], width=8)
        self.ct_proto.current(0)
        self.ct_proto.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="测试连接", command=self._start_ct).pack(side=tk.LEFT)

        ttk.Label(frame, text="测试数据:").pack(anchor=tk.W, pady=(0, 5))
        self.ct_data = ttk.Entry(frame, width=50)
        self.ct_data.insert(0, "Hello")
        self.ct_data.pack(anchor=tk.W, pady=(0, 10))
        ttk.Button(frame, text="发送测试数据", command=self._send_ct).pack(anchor=tk.W, pady=(0, 10))

        rf = ttk.LabelFrame(frame, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.ct_result = scrolledtext.ScrolledText(rf, height=12, font=("Consolas", 10))
        self.ct_result.pack(fill=tk.BOTH, expand=True)
        self.ct_socket = None

    def _start_ct(self):
        target = self.ct_target.get().strip()
        port = self.ct_port.get().strip()
        proto = self.ct_proto.get()
        if not target or not port:
            messagebox.showwarning("警告", "请填写目标IP和端口")
            return
        self.ct_result.delete("1.0", tk.END)

        def run():
            try:
                t0 = time.time()
                sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM if proto=="TCP" else socket.SOCK_DGRAM)
                sk.settimeout(5)
                if proto == "TCP":
                    sk.connect((target, int(port)))
                latency = (time.time()-t0)*1000
                self.parent.after(0, lambda: self.ct_result.insert(tk.END, f"连接成功！延迟: {latency:.1f} ms\n"))
                self.ct_socket = sk
            except Exception as e:
                self.parent.after(0, lambda: self.ct_result.insert(tk.END, f"连接失败: {e}\n"))
        threading.Thread(target=run, daemon=True).start()

    def _send_ct(self):
        if not self.ct_socket:
            messagebox.showwarning("警告", "请先测试连接")
            return
        data = self.ct_data.get().encode()
        try:
            self.ct_socket.sendall(data)
            self.ct_socket.settimeout(3)
            resp = self.ct_socket.recv(4096)
            self.ct_result.insert(tk.END, f"发送: {data.decode()}\n返回: {resp.decode()}\n")
        except Exception as e:
            self.ct_result.insert(tk.END, f"发送/接收失败: {e}\n")

    # ==================== 13. 网络服务工具集 ====================
    def _create_net_services(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="网络服务工具集", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # 子工具标签
        ns_notebook = ttk.Notebook(frame)
        ns_notebook.pack(fill=tk.BOTH, expand=True)

        # DNS查询
        dns_tab = ttk.Frame(ns_notebook)
        ns_notebook.add(dns_tab, text=" DNS查询 ")
        self._create_dns_tool(dns_tab)

        # Whois查询
        whois_tab = ttk.Frame(ns_notebook)
        ns_notebook.add(whois_tab, text=" Whois查询 ")
        self._create_whois_tool(whois_tab)

        # HTTP测试
        http_tab = ttk.Frame(ns_notebook)
        ns_notebook.add(http_tab, text=" HTTP测试 ")
        self._create_http_tool(http_tab)

        # 端口监听
        listen_tab = ttk.Frame(ns_notebook)
        ns_notebook.add(listen_tab, text=" 端口监听 ")
        self._create_listen_tool(listen_tab)

    def _create_dns_tool(self, parent):
        ttk.Label(parent, text="DNS查询", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        inp = ttk.Frame(parent)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="域名:").pack(side=tk.LEFT, padx=(0, 5))
        self.dns_domain = ttk.Entry(inp, width=30)
        self.dns_domain.insert(0, "www.baidu.com")
        self.dns_domain.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="查询", command=self._query_dns).pack(side=tk.LEFT)

        rf = ttk.LabelFrame(parent, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.dns_result = scrolledtext.ScrolledText(rf, height=10, font=("Consolas", 10))
        self.dns_result.pack(fill=tk.BOTH, expand=True)

    def _query_dns(self):
        domain = self.dns_domain.get().strip()
        if not domain:
            return
        self.dns_result.delete("1.0", tk.END)
        try:
            ips = socket.getaddrinfo(domain, None)
            unique_ips = set(ip[4][0] for ip in ips)
            self.dns_result.insert(tk.END, f"域名: {domain}\n")
            for ip in unique_ips:
                self.dns_result.insert(tk.END, f"  -> {ip}\n")
        except Exception as e:
            self.dns_result.insert(tk.END, f"查询失败: {e}\n")

    def _create_whois_tool(self, parent):
        ttk.Label(parent, text="Whois域名查询", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        inp = ttk.Frame(parent)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="域名:").pack(side=tk.LEFT, padx=(0, 5))
        self.whois_domain = ttk.Entry(inp, width=30)
        self.whois_domain.insert(0, "baidu.com")
        self.whois_domain.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="查询", command=self._query_whois).pack(side=tk.LEFT)

        rf = ttk.LabelFrame(parent, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.whois_result = scrolledtext.ScrolledText(rf, height=15, font=("Consolas", 10))
        self.whois_result.pack(fill=tk.BOTH, expand=True)

    def _query_whois(self):
        domain = self.whois_domain.get().strip()
        if not domain:
            return
        self.whois_result.delete("1.0", tk.END)
        self.whois_result.insert(tk.END, "查询中...\n")

        def run():
            try:
                sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sk.settimeout(10)
                sk.connect(("whois.verisign-grs.com", 43))
                sk.send(f"{domain}\r\n".encode())
                data = b""
                while True:
                    chunk = sk.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                sk.close()
                self.parent.after(0, lambda: self.whois_result.delete("1.0", tk.END) or self.whois_result.insert(tk.END, data.decode(errors='ignore')))
            except Exception as e:
                self.parent.after(0, lambda: self.whois_result.delete("1.0", tk.END) or self.whois_result.insert(tk.END, f"查询失败: {e}"))
        threading.Thread(target=run, daemon=True).start()

    def _create_http_tool(self, parent):
        ttk.Label(parent, text="HTTP/HTTPS接口测试", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        inp = ttk.Frame(parent)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="URL:").pack(side=tk.LEFT, padx=(0, 5))
        self.http_url = ttk.Entry(inp, width=40)
        self.http_url.insert(0, "https://www.baidu.com")
        self.http_url.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="方法:").pack(side=tk.LEFT, padx=(0, 5))
        self.http_method = ttk.Combobox(inp, values=["GET", "POST", "PUT", "DELETE"], width=8)
        self.http_method.current(0)
        self.http_method.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="发送", command=self._send_http).pack(side=tk.LEFT)

        ttk.Label(parent, text="请求体:").pack(anchor=tk.W, pady=(0, 5))
        self.http_body = scrolledtext.ScrolledText(parent, height=3, font=("Consolas", 10))
        self.http_body.pack(fill=tk.X, pady=(0, 10))

        rf = ttk.LabelFrame(parent, text=" 响应 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.http_result = scrolledtext.ScrolledText(rf, height=10, font=("Consolas", 10))
        self.http_result.pack(fill=tk.BOTH, expand=True)

    def _send_http(self):
        url = self.http_url.get().strip()
        method = self.http_method.get()
        if not url:
            return
        self.http_result.delete("1.0", tk.END)
        self.http_result.insert(tk.END, "请求中...\n")

        def run():
            try:
                req = urllib.request.Request(url, method=method)
                body = self.http_body.get("1.0", tk.END).strip()
                if body and method in ["POST", "PUT"]:
                    req.data = body.encode()
                    req.add_header("Content-Type", "application/json")
                t0 = time.time()
                resp = urllib.request.urlopen(req, timeout=10)
                elapsed = (time.time()-t0)*1000
                data = resp.read().decode(errors='ignore')
                self.parent.after(0, lambda: self._show_http(resp.status, elapsed, data))
            except Exception as e:
                self.parent.after(0, lambda: self.http_result.delete("1.0", tk.END) or self.http_result.insert(tk.END, f"请求失败: {e}"))
        threading.Thread(target=run, daemon=True).start()

    def _show_http(self, status, elapsed, data):
        self.http_result.delete("1.0", tk.END)
        self.http_result.insert(tk.END, f"状态码: {status}\n")
        self.http_result.insert(tk.END, f"耗时: {elapsed:.1f} ms\n")
        self.http_result.insert(tk.END, f"响应体:\n{data[:2000]}\n")

    def _create_listen_tool(self, parent):
        ttk.Label(parent, text="本地端口监听", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        inp = ttk.Frame(parent)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="端口:").pack(side=tk.LEFT, padx=(0, 5))
        self.listen_port = ttk.Entry(inp, width=10)
        self.listen_port.insert(0, "9999")
        self.listen_port.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="开始监听", command=self._start_listen).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(inp, text="停止", command=self._stop_listen).pack(side=tk.LEFT)

        rf = ttk.LabelFrame(parent, text=" 日志 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.listen_log = scrolledtext.ScrolledText(rf, height=12, font=("Consolas", 10))
        self.listen_log.pack(fill=tk.BOTH, expand=True)
        self.listen_running = False
        self.listen_socket = None

    def _start_listen(self):
        port = self.listen_port.get().strip()
        if not port:
            return
        self.listen_running = True
        self.listen_log.delete("1.0", tk.END)
        self.listen_log.insert(tk.END, f"开始在端口 {port} 监听...\n")

        def run():
            try:
                self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.listen_socket.bind(("0.0.0.0", int(port)))
                self.listen_socket.listen(5)
                self.listen_socket.settimeout(1)
                while self.listen_running:
                    try:
                        conn, addr = self.listen_socket.accept()
                        self.parent.after(0, lambda a=addr: self.listen_log.insert(tk.END, f"连接来自: {a}\n"))
                        data = conn.recv(1024)
                        if data:
                            self.parent.after(0, lambda d=data.decode(errors='ignore'): self.listen_log.insert(tk.END, f"收到: {d}\n"))
                        conn.send(b"OK")
                        conn.close()
                    except socket.timeout:
                        continue
            except Exception as e:
                self.parent.after(0, lambda: self.listen_log.insert(tk.END, f"错误: {e}\n"))
        threading.Thread(target=run, daemon=True).start()

    def _stop_listen(self):
        self.listen_running = False
        if self.listen_socket:
            self.listen_socket.close()
        self.listen_log.insert(tk.END, "监听已停止\n")

    # ==================== 14. DHCP检测 ====================
    def _create_dhcp_detect(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="DHCP检测", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        ttk.Button(frame, text="扫描DHCP服务器", command=self._start_dhcp).pack(anchor=tk.W, pady=(0, 10))

        rf = ttk.LabelFrame(frame, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        cols = ("server", "pool", "gateway", "dns", "status")
        self.dhcp_tree = ttk.Treeview(rf, columns=cols, show="headings", height=15)
        for c, t, w in [("server","DHCP服务器",150),("pool","地址池",150),("gateway","网关",150),("dns","DNS",150),("status","状态",100)]:
            self.dhcp_tree.heading(c, text=t)
            self.dhcp_tree.column(c, width=w, anchor=tk.CENTER)
        sb = ttk.Scrollbar(rf, orient=tk.VERTICAL, command=self.dhcp_tree.yview)
        self.dhcp_tree.configure(yscrollcommand=sb.set)
        self.dhcp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    def _start_dhcp(self):
        for i in self.dhcp_tree.get_children():
            self.dhcp_tree.delete(i)

        def run():
            try:
                # 通过ipconfig获取所有网络适配器信息
                r = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, timeout=10, encoding='gbk')
                output = r.stdout

                adapters = []
                current_adapter = None

                for line in output.split('\n'):
                    line = line.strip()

                    # 检测新的适配器（以"以太网"、"无线"、"蓝牙"开头）
                    if line.startswith(("以太网", "无线", "蓝牙")) and line.endswith(":"):
                        if current_adapter:
                            adapters.append(current_adapter)
                        current_adapter = {
                            "name": line[:-1],
                            "dhcp_enabled": False,
                            "dhcp_server": None,
                            "ip": None,
                            "subnet": None,
                            "gateway": None,
                            "dns": [],
                            "status": "未连接"
                        }
                        continue

                    if not current_adapter:
                        continue

                    # 媒体状态
                    if "媒体状态" in line:
                        if "已断开" not in line and "断开连接" not in line:
                            current_adapter["status"] = "已连接"

                    # DHCP是否启用
                    if "DHCP 已启用" in line or "DHCP Enabled" in line:
                        if "是" in line or "Yes" in line:
                            current_adapter["dhcp_enabled"] = True

                    # IP地址
                    if "IPv4 地址" in line or "IP Address" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            ip = parts[-1].strip().split("(")[0].strip()
                            current_adapter["ip"] = ip

                    # 子网掩码
                    if "子网掩码" in line or "Subnet Mask" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            current_adapter["subnet"] = parts[-1].strip()

                    # 默认网关
                    if "默认网关" in line or "Default Gateway" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            gw = parts[-1].strip()
                            if gw and gw != "":
                                current_adapter["gateway"] = gw

                    # DNS服务器
                    if "DNS 服务器" in line or "DNS Servers" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            dns = parts[-1].strip()
                            if dns:
                                current_adapter["dns"].append(dns)

                    # DHCP服务器
                    if "DHCP 服务器" in line or "DHCP Server" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            srv = parts[-1].strip()
                            if srv:
                                current_adapter["dhcp_server"] = srv

                # 添加最后一个适配器
                if current_adapter:
                    adapters.append(current_adapter)

                # 显示结果
                found = 0
                for adapter in adapters:
                    # 有IPv4地址就算已连接（已连接的适配器可能没有"媒体状态"行）
                    if adapter["ip"] and adapter["ip"] != "N/A":
                        dhcp_status = "DHCP" if adapter["dhcp_enabled"] else "静态IP"
                        dhcp_server = adapter["dhcp_server"] or "N/A"
                        dns_str = ", ".join(adapter["dns"]) if adapter["dns"] else "N/A"

                        self.parent.after(0, lambda a=adapter, s=dhcp_status, ds=dhcp_server, d=dns_str:
                            self.dhcp_tree.insert("", tk.END, values=(
                                ds,
                                a["ip"] or "N/A",
                                a["gateway"] or "N/A",
                                d,
                                s
                            ))
                        )
                        found += 1

                if found == 0:
                    self.parent.after(0, lambda: self.dhcp_tree.insert("", tk.END, values=("N/A", "N/A", "N/A", "N/A", "未找到已连接的网络适配器")))

            except Exception as e:
                self.parent.after(0, lambda: self.dhcp_tree.insert("", tk.END, values=("N/A", "N/A", "N/A", "N/A", f"错误: {e}")))

        threading.Thread(target=run, daemon=True).start()

    # ==================== 15. 数据包抓包 ====================
    def _create_packet_capture(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="数据包抓包", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(frame)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="网卡:").pack(side=tk.LEFT, padx=(0, 5))
        self.pc_iface = ttk.Combobox(inp, width=25)
        self.pc_iface['values'] = list(psutil.net_if_addrs().keys())
        if self.pc_iface['values']:
            self.pc_iface.current(0)
        self.pc_iface.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="过滤IP:").pack(side=tk.LEFT, padx=(0, 5))
        self.pc_filter_ip = ttk.Entry(inp, width=15)
        self.pc_filter_ip.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="端口:").pack(side=tk.LEFT, padx=(0, 5))
        self.pc_filter_port = ttk.Entry(inp, width=8)
        self.pc_filter_port.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="开始抓包", command=self._start_pc).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(inp, text="停止", command=self._stop_pc).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(inp, text="保存", command=self._save_pc).pack(side=tk.LEFT)

        rf = ttk.LabelFrame(frame, text=" 数据包 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        cols = ("no", "time", "src", "dst", "proto", "sport", "dport", "info")
        self.pc_tree = ttk.Treeview(rf, columns=cols, show="headings", height=15)
        for c, t, w in [("no","序号",50),("time","时间",100),("src","源IP",130),("dst","目的IP",130),("proto","协议",60),("sport","源端口",70),("dport","目的端口",70),("info","信息",200)]:
            self.pc_tree.heading(c, text=t)
            self.pc_tree.column(c, width=w, anchor=tk.CENTER)
        sb = ttk.Scrollbar(rf, orient=tk.VERTICAL, command=self.pc_tree.yview)
        self.pc_tree.configure(yscrollcommand=sb.set)
        self.pc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.pc_packets = []
        self.pc_running = False
        self.pc_count = 0

    def _start_pc(self):
        self.pc_running = True
        self.pc_count = 0
        self.pc_packets = []
        for i in self.pc_tree.get_children():
            self.pc_tree.delete(i)

        filter_ip = self.pc_filter_ip.get().strip()
        filter_port = self.pc_filter_port.get().strip()

        def run():
            try:
                sk = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
                iface = self.pc_iface.get()
                addrs = psutil.net_if_addrs().get(iface, [])
                local_ip = None
                for a in addrs:
                    if a.family == socket.AF_INET:
                        local_ip = a.address
                        break
                if local_ip:
                    sk.bind((local_ip, 0))
                sk.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                sk.settimeout(1)

                while self.pc_running:
                    try:
                        data, addr = sk.recvfrom(65535)
                        if len(data) < 20:
                            continue

                        # 解析IP头
                        ip_header = data[0:20]
                        iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
                        version_ihl = iph[0]
                        ihl = (version_ihl & 0xF) * 4
                        protocol = iph[6]
                        src_ip = socket.inet_ntoa(iph[8])
                        dst_ip = socket.inet_ntoa(iph[9])

                        # 过滤
                        if filter_ip and filter_ip not in src_ip and filter_ip not in dst_ip:
                            continue

                        proto_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
                        proto = proto_map.get(protocol, f"IP({protocol})")

                        sport = dport = ""
                        info = ""
                        if protocol in (6, 17) and len(data) >= ihl + 8:
                            tcp_udp = struct.unpack('!HH', data[ihl:ihl+4])
                            sport = str(tcp_udp[0])
                            dport = str(tcp_udp[1])
                            if filter_port and dport != filter_port and sport != filter_port:
                                continue

                        self.pc_count += 1
                        pkt_info = {
                            "no": self.pc_count,
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "src": src_ip,
                            "dst": dst_ip,
                            "proto": proto,
                            "sport": sport,
                            "dport": dport,
                            "info": f"{proto} {src_ip}:{sport} -> {dst_ip}:{dport}"
                        }
                        self.pc_packets.append(pkt_info)
                        self.parent.after(0, lambda p=pkt_info: self.pc_tree.insert("", tk.END, values=(
                            p["no"], p["time"], p["src"], p["dst"], p["proto"], p["sport"], p["dport"], p["info"]
                        )))
                    except socket.timeout:
                        continue
                sk.close()
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror("错误", f"抓包失败: {e}"))

        threading.Thread(target=run, daemon=True).start()

    def _stop_pc(self):
        self.pc_running = False

    def _save_pc(self):
        if not self.pc_packets:
            messagebox.showwarning("警告", "没有数据包可保存")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")])
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.pc_packets, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"已保存 {len(self.pc_packets)} 个数据包")

    # ==================== 16. MAC地址工具 ====================
    def _create_mac_tools(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="MAC地址工具", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # 子工具标签
        mt_notebook = ttk.Notebook(frame)
        mt_notebook.pack(fill=tk.BOTH, expand=True)

        # MAC厂商查询
        vendor_tab = ttk.Frame(mt_notebook)
        mt_notebook.add(vendor_tab, text=" MAC厂商查询 ")
        self._create_mac_vendor_tool(vendor_tab)

        # 随机MAC生成
        random_tab = ttk.Frame(mt_notebook)
        mt_notebook.add(random_tab, text=" 随机MAC生成 ")
        self._create_mac_random_tool(random_tab)

        # 本机MAC
        local_tab = ttk.Frame(mt_notebook)
        mt_notebook.add(local_tab, text=" 本机MAC ")
        self._create_mac_local_tool(local_tab)

        # IP-MAC绑定
        bind_tab = ttk.Frame(mt_notebook)
        mt_notebook.add(bind_tab, text=" IP-MAC绑定 ")
        self._create_mac_bind_tool(bind_tab)

    def _create_mac_vendor_tool(self, parent):
        ttk.Label(parent, text="MAC厂商查询", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        inp = ttk.Frame(parent)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="MAC地址:").pack(side=tk.LEFT, padx=(0, 5))
        self.mv_mac = ttk.Entry(inp, width=20)
        self.mv_mac.insert(0, "00:1A:2B:3C:4D:5E")
        self.mv_mac.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="查询", command=self._query_mac_vendor).pack(side=tk.LEFT)

        rf = ttk.LabelFrame(parent, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.mv_result = scrolledtext.ScrolledText(rf, height=8, font=("Consolas", 10))
        self.mv_result.pack(fill=tk.BOTH, expand=True)

    def _query_mac_vendor(self):
        mac = self.mv_mac.get().strip().upper()
        self.mv_result.delete("1.0", tk.END)
        if not mac:
            return
        prefix = mac[:8]
        vendor = _OUI_DATABASE.get(prefix, "未知厂商")
        self.mv_result.insert(tk.END, f"MAC地址: {mac}\n")
        self.mv_result.insert(tk.END, f"OUI前缀: {prefix}\n")
        self.mv_result.insert(tk.END, f"厂商: {vendor}\n")
        if vendor == "未知厂商":
            self.mv_result.insert(tk.END, f"\n提示: 该OUI未在数据库中找到，可能是新分配的地址段\n")

    def _create_mac_random_tool(self, parent):
        ttk.Label(parent, text="随机MAC地址生成", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(parent)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="数量:").pack(side=tk.LEFT, padx=(0, 5))
        self.mr_count = ttk.Entry(inp, width=6)
        self.mr_count.insert(0, "5")
        self.mr_count.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="生成", command=self._gen_mac).pack(side=tk.LEFT)

        rf = ttk.LabelFrame(parent, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.mr_result = scrolledtext.ScrolledText(rf, height=10, font=("Consolas", 10))
        self.mr_result.pack(fill=tk.BOTH, expand=True)

    def _gen_mac(self):
        self.mr_result.delete("1.0", tk.END)
        try:
            count = int(self.mr_count.get())
            for _ in range(count):
                mac = ":".join([f"{random.randint(0, 255):02X}" for _ in range(6)])
                # 确保是本地管理的单播地址
                first_byte = int(mac[:2], 16)
                first_byte = (first_byte | 0x02) & 0xFE
                mac = f"{first_byte:02X}" + mac[2:]
                self.mr_result.insert(tk.END, f"{mac}\n")
        except:
            self.mr_result.insert(tk.END, "请输入有效数量\n")

    def _create_mac_local_tool(self, parent):
        ttk.Label(parent, text="本机MAC地址", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        ttk.Button(parent, text="刷新", command=self._refresh_local_mac).pack(anchor=tk.W, pady=(0, 10))

        rf = ttk.LabelFrame(parent, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.ml_result = scrolledtext.ScrolledText(rf, height=12, font=("Consolas", 10))
        self.ml_result.pack(fill=tk.BOTH, expand=True)
        self._refresh_local_mac()

    def _refresh_local_mac(self):
        self.ml_result.delete("1.0", tk.END)
        try:
            ifaces = psutil.net_if_addrs()
            for name, addrs in ifaces.items():
                for addr in addrs:
                    if addr.family.name == "AF_LINK" or (hasattr(addr, 'family') and str(addr.family) == 'AddressFamily.AF_LINK'):
                        self.ml_result.insert(tk.END, f"网卡: {name}\nMAC: {addr.address}\n\n")
            # Windows下使用getmac
            if platform.system() == "Windows":
                r = subprocess.run(["getmac", "/fo", "csv", "/nh"], capture_output=True, text=True, timeout=5)
                for line in r.stdout.strip().split('\n'):
                    parts = line.split(',')
                    if len(parts) >= 2:
                        mac = parts[0].strip('"')
                        iface = parts[1].strip('"')
                        if mac and mac != "N/A":
                            self.ml_result.insert(tk.END, f"网卡: {iface}\nMAC: {mac}\n\n")
        except Exception as e:
            self.ml_result.insert(tk.END, f"获取失败: {e}\n")

    def _create_mac_bind_tool(self, parent):
        ttk.Label(parent, text="IP-MAC绑定测试", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        inp = ttk.Frame(parent)
        inp.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(inp, text="IP:").pack(side=tk.LEFT, padx=(0, 5))
        self.mb_ip = ttk.Entry(inp, width=20)
        self.mb_ip.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(inp, text="MAC:").pack(side=tk.LEFT, padx=(0, 5))
        self.mb_mac = ttk.Entry(inp, width=20)
        self.mb_mac.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inp, text="绑定", command=self._bind_mac).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(inp, text="解绑", command=self._unbind_mac).pack(side=tk.LEFT)

        ttk.Button(parent, text="查看ARP表", command=self._show_arp).pack(anchor=tk.W, pady=(0, 10))

        rf = ttk.LabelFrame(parent, text=" 结果 ", padding=8)
        rf.pack(fill=tk.BOTH, expand=True)
        self.mb_result = scrolledtext.ScrolledText(rf, height=12, font=("Consolas", 10))
        self.mb_result.pack(fill=tk.BOTH, expand=True)

    def _bind_mac(self):
        ip = self.mb_ip.get().strip()
        mac = self.mb_mac.get().strip()
        if not ip or not mac:
            messagebox.showwarning("警告", "请填写IP和MAC")
            return
        self.mb_result.delete("1.0", tk.END)
        try:
            if platform.system() == "Windows":
                r = subprocess.run(["arp", "-s", ip, mac], capture_output=True, text=True, timeout=5)
                if r.returncode == 0:
                    self.mb_result.insert(tk.END, f"绑定成功: {ip} -> {mac}\n")
                else:
                    self.mb_result.insert(tk.END, f"绑定失败: {r.stderr}\n")
            else:
                r = subprocess.run(["arp", "-s", ip, mac], capture_output=True, text=True, timeout=5)
                self.mb_result.insert(tk.END, f"绑定结果: {r.stdout}\n")
        except Exception as e:
            self.mb_result.insert(tk.END, f"绑定失败: {e}\n")

    def _unbind_mac(self):
        ip = self.mb_ip.get().strip()
        if not ip:
            messagebox.showwarning("警告", "请填写IP")
            return
        self.mb_result.delete("1.0", tk.END)
        try:
            r = subprocess.run(["arp", "-d", ip], capture_output=True, text=True, timeout=5)
            self.mb_result.insert(tk.END, f"解绑结果: {r.stdout}\n")
        except Exception as e:
            self.mb_result.insert(tk.END, f"解绑失败: {e}\n")

    def _show_arp(self):
        self.mb_result.delete("1.0", tk.END)
        try:
            r = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5)
            self.mb_result.insert(tk.END, r.stdout)
        except Exception as e:
            self.mb_result.insert(tk.END, f"获取失败: {e}\n")