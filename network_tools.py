import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import ipaddress
import struct
import socket
import math
import binascii
import threading

class NetworkToolsPage:
    def __init__(self, parent, main_app=None):
        self.parent = parent
        self.main_app = main_app  # 引用主应用以获取AI配置
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # 主容器 - 左右分栏
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # 左侧工具导航面板
        nav_panel = ttk.Frame(main_container, width=180)
        nav_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        nav_panel.pack_propagate(False)
        
        # 右侧内容面板
        self.content_panel = ttk.Frame(main_container)
        self.content_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 工具列表
        self.tools = [
            ("子网计算器", self.create_subnet_calculator),
            ("VLSM计算器", self.create_vlsm_calculator),
            ("IP格式转换", self.create_ip_converter),
            ("路由汇总", self.create_route_summarization),
            ("通配符掩码", self.create_wildcard_mask),
            ("IP地址分类", self.create_ip_classification),
            ("VLAN计算", self.create_vlan_calculator),
            ("带宽计算", self.create_bandwidth_calculator),
            ("端口查询", self.create_port_lookup),
            ("MAC地址工具", self.create_mac_tools),
            ("OSPF Cost", self.create_ospf_cost),
            ("CRC校验", self.create_crc_calculator),
        ]
        
        # 创建导航按钮
        nav_title = ttk.Label(nav_panel, text="网络工具", font=("Microsoft YaHei", 12, "bold"))
        nav_title.pack(pady=(10, 10))
        
        self.nav_buttons = []
        self.tool_frames = {}
        
        for name, create_func in self.tools:
            btn = ttk.Button(nav_panel, text=name, width=18,
                           command=lambda n=name: self.switch_tool(n))
            btn.pack(fill=tk.X, padx=5, pady=2)
            self.nav_buttons.append((name, btn))
            
            tool_frame = ttk.Frame(self.content_panel)
            self.tool_frames[name] = tool_frame
            create_func(tool_frame)
        
        # 分隔线
        ttk.Separator(nav_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        
        # AI协助按钮
        ai_btn = ttk.Button(nav_panel, text="AI协助", width=18,
                          command=self.open_ai_assistant, style="Accent.TButton")
        ai_btn.pack(fill=tk.X, padx=5, pady=2)
        
        self.current_tool = None
        self.switch_tool(self.tools[0][0])
        
    def switch_tool(self, name):
        if self.current_tool and self.current_tool in self.tool_frames:
            self.tool_frames[self.current_tool].pack_forget()
            
        if name in self.tool_frames:
            self.tool_frames[name].pack(fill=tk.BOTH, expand=True)
            self.current_tool = name
            
    def create_subnet_calculator(self, parent):
        title = ttk.Label(parent, text="子网计算器", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="输入IP地址和子网掩码，自动计算网络地址、广播地址、可用主机等信息", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="输入参数", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(row1, text="IP地址:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.subnet_ip = ttk.Entry(row1, width=20)
        self.subnet_ip.insert(0, "192.168.1.0")
        self.subnet_ip.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(row1, text="子网掩码/CIDR:", width=15).pack(side=tk.LEFT, padx=(0, 5))
        self.subnet_mask = ttk.Entry(row1, width=15)
        self.subnet_mask.insert(0, "/24")
        self.subnet_mask.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row1, text="计算", command=self.calculate_subnet, width=10).pack(side=tk.LEFT)
        
        div_frame = ttk.LabelFrame(parent, text="子网划分", padding="15")
        div_frame.pack(fill=tk.X, padx=20, pady=10)
        
        div_row = ttk.Frame(div_frame)
        div_row.pack(fill=tk.X)
        
        ttk.Label(div_row, text="划分子网数:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.subnet_count = ttk.Entry(div_row, width=10)
        self.subnet_count.insert(0, "4")
        self.subnet_count.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(div_row, text="划分子网", command=self.divide_subnet, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="计算结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.subnet_result = scrolledtext.ScrolledText(result_frame, height=18, font=("Consolas", 10))
        self.subnet_result.pack(fill=tk.BOTH, expand=True)
        
    def calculate_subnet(self):
        try:
            ip_input = self.subnet_ip.get().strip()
            mask_input = self.subnet_mask.get().strip()
            
            if mask_input.startswith('/'):
                network = ipaddress.ip_network(f"{ip_input}{mask_input}", strict=False)
            elif '.' in mask_input:
                network = ipaddress.ip_network(f"{ip_input}/{mask_input}", strict=False)
            else:
                network = ipaddress.ip_network(f"{ip_input}/{mask_input}", strict=False)
            
            network_addr = network.network_address
            broadcast_addr = network.broadcast_address
            netmask = network.netmask
            wildcard = ipaddress.ip_address(int(ipaddress.ip_address('255.255.255.255')) - int(netmask))
            total_hosts = network.num_addresses
            usable_hosts = total_hosts - 2 if network.prefixlen < 31 else total_hosts
            first_host = network_addr + 1 if network.prefixlen < 31 else network_addr
            last_host = broadcast_addr - 1 if network.prefixlen < 31 else broadcast_addr
            network_class = self._get_ip_class(str(network_addr))
            ip_type = "私有地址" if network_addr.is_private else "公有地址"
            
            ip_bin = bin(int(network_addr))[2:].zfill(32)
            mask_bin = bin(int(netmask))[2:].zfill(32)
            
            result = f"""
===========================================================
                    子网计算结果
===========================================================

【网络信息】
  网络地址:      {network_addr}
  广播地址:      {broadcast_addr}
  子网掩码:      {netmask}
  通配符掩码:    {wildcard}
  CIDR表示:      /{network.prefixlen}
  
【主机信息】
  可用主机数:    {usable_hosts:,}
  总地址数:      {total_hosts:,}
  第一个可用IP:  {first_host}
  最后一个可用IP: {last_host}
  
【地址分类】
  IP地址类别:    {network_class}
  地址类型:      {ip_type}
  是否组播:      {'是' if network_addr.is_multicast else '否'}
  是否环回:      {'是' if network_addr.is_loopback else '否'}
  是否链路本地:  {'是' if network_addr.is_link_local else '否'}
  
【二进制表示】
  IP地址:        {ip_bin[:8]}.{ip_bin[8:16]}.{ip_bin[16:24]}.{ip_bin[24:32]}
  子网掩码:      {mask_bin[:8]}.{mask_bin[8:16]}.{mask_bin[16:24]}.{mask_bin[24:32]}
  
【十六进制表示】
  IP地址:        {hex(int(network_addr))}
  子网掩码:      {hex(int(netmask))}
  
===========================================================
"""
            self.subnet_result.delete("1.0", tk.END)
            self.subnet_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"计算失败: {str(e)}")
            
    def divide_subnet(self):
        try:
            ip_input = self.subnet_ip.get().strip()
            mask_input = self.subnet_mask.get().strip()
            count = int(self.subnet_count.get())
            
            if mask_input.startswith('/'):
                network = ipaddress.ip_network(f"{ip_input}{mask_input}", strict=False)
            else:
                network = ipaddress.ip_network(f"{ip_input}/{mask_input}", strict=False)
            
            bits_needed = math.ceil(math.log2(count))
            new_prefix = network.prefixlen + bits_needed
            
            if new_prefix > 32:
                messagebox.showerror("错误", "子网数过多，超出IPv4地址范围")
                return
            
            subnets = list(network.subnets(new_prefix=new_prefix))[:count]
            
            result = f"\n{'='*80}\n"
            result += f"将 {network} 划分为 {count} 个子网 (借{bits_needed}位，新掩码 /{new_prefix})\n"
            result += f"{'='*80}\n\n"
            result += f"{'序号':<6} {'子网地址':<20} {'子网掩码':<18} {'可用主机范围':<40} {'广播地址':<18} {'主机数':<10}\n"
            result += "-" * 120 + "\n"
            
            for i, subnet in enumerate(subnets):
                first = subnet.network_address + 1
                last = subnet.broadcast_address - 1
                hosts = subnet.num_addresses - 2
                result += f"{i+1:<6} {str(subnet.network_address):<20} {str(subnet.netmask):<18} {str(first)} - {str(last):<18} {str(subnet.broadcast_address):<18} {hosts:<10}\n"
            
            result += f"\n{'='*80}\n"
            
            self.subnet_result.insert(tk.END, result)
            
        except Exception as e:
            messagebox.showerror("错误", f"划分失败: {str(e)}")
            
    def _get_ip_class(self, ip_str):
        first_octet = int(ip_str.split('.')[0])
        if first_octet < 128:
            return "A类 (1.0.0.0 - 126.255.255.255)"
        elif first_octet < 192:
            return "B类 (128.0.0.0 - 191.255.255.255)"
        elif first_octet < 224:
            return "C类 (192.0.0.0 - 223.255.255.255)"
        elif first_octet < 240:
            return "D类 (组播) (224.0.0.0 - 239.255.255.255)"
        else:
            return "E类 (保留) (240.0.0.0 - 255.255.255.255)"
            
    def create_vlsm_calculator(self, parent):
        title = ttk.Label(parent, text="VLSM计算器", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="根据各部门主机数量需求，自动计算最优子网划分方案", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="输入参数", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(row1, text="网络地址:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.vlsm_network = ttk.Entry(row1, width=20)
        self.vlsm_network.insert(0, "192.168.1.0/24")
        self.vlsm_network.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(row1, text="子网需求 (每行: 名称,主机数):", width=25).pack(side=tk.LEFT)
        
        self.vlsm_requirements = scrolledtext.ScrolledText(input_frame, height=6, width=50, font=("Consolas", 10))
        self.vlsm_requirements.insert("1.0", "销售部,50\n技术部,30\n财务部,20\n人事部,10\n访客网络,5")
        self.vlsm_requirements.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Button(input_frame, text="计算VLSM", command=self.calculate_vlsm, width=15).pack()
        
        result_frame = ttk.LabelFrame(parent, text="VLSM计算结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.vlsm_result = scrolledtext.ScrolledText(result_frame, height=15, font=("Consolas", 10))
        self.vlsm_result.pack(fill=tk.BOTH, expand=True)
        
    def calculate_vlsm(self):
        try:
            network = ipaddress.ip_network(self.vlsm_network.get().strip(), strict=False)
            requirements_text = self.vlsm_requirements.get("1.0", tk.END).strip()
            
            requirements = []
            for line in requirements_text.split('\n'):
                line = line.strip()
                if ',' in line:
                    name, hosts = line.split(',')
                    requirements.append((name.strip(), int(hosts.strip())))
            
            requirements.sort(key=lambda x: x[1], reverse=True)
            
            result = f"\n{'='*100}\n"
            result += f"VLSM计算 - 网络: {network}\n"
            result += f"{'='*100}\n\n"
            result += f"{'子网名称':<15} {'需要主机':<10} {'子网地址':<20} {'CIDR':<8} {'子网掩码':<18} {'可用IP范围':<45} {'广播地址':<18}\n"
            result += "-" * 140 + "\n"
            
            current_network = network
            
            for name, hosts in requirements:
                bits_needed = math.ceil(math.log2(hosts + 2))
                new_prefix = 32 - bits_needed
                
                subnet_size = 2 ** bits_needed
                network_int = int(current_network.network_address)
                aligned_network = network_int & ~(subnet_size - 1)
                new_network = ipaddress.ip_network(f"{ipaddress.ip_address(aligned_network)}/{new_prefix}", strict=False)
                
                first_host = new_network.network_address + 1
                last_host = new_network.broadcast_address - 1
                
                result += f"{name:<15} {hosts:<10} {str(new_network.network_address):<20} /{new_network.prefixlen:<7} {str(new_network.netmask):<18} {str(first_host)} - {str(last_host):<22} {str(new_network.broadcast_address):<18}\n"
                
                next_addr = int(new_network.broadcast_address) + 1
                current_network = ipaddress.ip_network(f"{ipaddress.ip_address(next_addr)}/{current_network.prefixlen}", strict=False)
            
            result += f"\n{'='*100}\n"
            
            self.vlsm_result.delete("1.0", tk.END)
            self.vlsm_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"VLSM计算失败: {str(e)}")
            
    def create_ip_converter(self, parent):
        title = ttk.Label(parent, text="IP格式转换", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="将IP地址转换为二进制、十六进制、八进制等多种格式", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="输入IP地址", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row = ttk.Frame(input_frame)
        row.pack(fill=tk.X)
        
        ttk.Label(row, text="IP地址:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.convert_ip = ttk.Entry(row, width=20)
        self.convert_ip.insert(0, "192.168.1.100")
        self.convert_ip.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row, text="转换", command=self.convert_ip_address, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="转换结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.convert_result = scrolledtext.ScrolledText(result_frame, height=18, font=("Consolas", 10))
        self.convert_result.pack(fill=tk.BOTH, expand=True)
        
    def convert_ip_address(self):
        try:
            ip_str = self.convert_ip.get().strip()
            ip = ipaddress.ip_address(ip_str)
            ip_int = int(ip)
            
            binary = bin(ip_int)[2:].zfill(32)
            hex_str = hex(ip_int)
            octal = oct(ip_int)
            
            packed = ip.packed
            hex_bytes = '.'.join(f'{b:02X}' for b in packed)
            reversed_ip = ipaddress.ip_address(int.from_bytes(packed[::-1], 'big'))
            ipv6_mapped = f"::ffff:{ip_str}"
            
            result = f"""
===========================================================
                  IP地址格式转换
===========================================================

【十进制点分表示】
  {ip_str}

【二进制表示】
  {binary[:8]}.{binary[8:16]}.{binary[16:24]}.{binary[24:32]}

【十六进制表示】
  {hex_str}

【八进制表示】
  {octal}

【十六进制字节表示】
  {hex_bytes}

【十进制整数表示】
  {ip_int:,}

【IPv4映射IPv6表示】
  {ipv6_mapped}

【反向字节序IP】
  {reversed_ip}

【URL编码表示】
  %{ip_str.replace('.', '%2E')}

===========================================================
"""
            self.convert_result.delete("1.0", tk.END)
            self.convert_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
            
    def create_route_summarization(self, parent):
        title = ttk.Label(parent, text="路由汇总", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="输入多条路由，自动汇总为最简路由表，减少路由条目", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="输入路由 (每行一个CIDR)", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.routes_input = scrolledtext.ScrolledText(input_frame, height=6, width=50, font=("Consolas", 10))
        self.routes_input.insert("1.0", "192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24\n192.168.3.0/24")
        self.routes_input.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(input_frame, text="计算汇总路由", command=self.calculate_route_summary, width=15).pack()
        
        result_frame = ttk.LabelFrame(parent, text="汇总结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.route_result = scrolledtext.ScrolledText(result_frame, height=15, font=("Consolas", 10))
        self.route_result.pack(fill=tk.BOTH, expand=True)
        
    def calculate_route_summary(self):
        try:
            routes_text = self.routes_input.get("1.0", tk.END).strip()
            networks = []
            
            for line in routes_text.split('\n'):
                line = line.strip()
                if line:
                    networks.append(ipaddress.ip_network(line, strict=False))
            
            summarized = list(ipaddress.collapse_addresses(networks))
            
            result = f"\n{'='*80}\n"
            result += f"路由汇总计算\n"
            result += f"{'='*80}\n\n"
            result += "【原始路由】\n"
            for net in networks:
                result += f"  {net}\n"
            
            result += f"\n【汇总后的路由】\n"
            for net in summarized:
                result += f"  {net}\n"
            
            result += f"\n汇总前: {len(networks)} 条路由"
            result += f"\n汇总后: {len(summarized)} 条路由"
            result += f"\n减少: {len(networks) - len(summarized)} 条路由\n"
            result += f"\n{'='*80}\n"
            
            self.route_result.delete("1.0", tk.END)
            self.route_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"路由汇总失败: {str(e)}")
            
    def create_wildcard_mask(self, parent):
        title = ttk.Label(parent, text="通配符掩码", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="子网掩码与通配符掩码互转，提供ACL配置示例", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="输入子网掩码", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row = ttk.Frame(input_frame)
        row.pack(fill=tk.X)
        
        ttk.Label(row, text="子网掩码:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.wildcard_mask = ttk.Entry(row, width=20)
        self.wildcard_mask.insert(0, "255.255.255.0")
        self.wildcard_mask.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row, text="计算", command=self.calculate_wildcard, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="计算结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.wildcard_result = scrolledtext.ScrolledText(result_frame, height=15, font=("Consolas", 10))
        self.wildcard_result.pack(fill=tk.BOTH, expand=True)
        
    def calculate_wildcard(self):
        try:
            mask_str = self.wildcard_mask.get().strip()
            mask = ipaddress.ip_address(mask_str)
            wildcard = ipaddress.ip_address(0xFFFFFFFF ^ int(mask))
            
            common_masks = {
                "255.0.0.0": "/8", "255.128.0.0": "/9", "255.192.0.0": "/10",
                "255.224.0.0": "/11", "255.240.0.0": "/12", "255.248.0.0": "/13",
                "255.252.0.0": "/14", "255.254.0.0": "/15", "255.255.0.0": "/16",
                "255.255.128.0": "/17", "255.255.192.0": "/18", "255.255.224.0": "/19",
                "255.255.240.0": "/20", "255.255.248.0": "/21", "255.255.252.0": "/22",
                "255.255.254.0": "/23", "255.255.255.0": "/24", "255.255.255.128": "/25",
                "255.255.255.192": "/26", "255.255.255.224": "/27", "255.255.255.240": "/28",
                "255.255.255.248": "/29", "255.255.255.252": "/30",
                "255.255.255.254": "/31", "255.255.255.255": "/32",
            }
            
            cidr = common_masks.get(mask_str, f"/{bin(int(mask)).count('1')}")
            
            result = f"""
===========================================================
                通配符掩码计算
===========================================================

【子网掩码】
  {mask_str}  ({cidr})

【通配符掩码】
  {wildcard}

【二进制对照】
  子网掩码:   {bin(int(mask))[2:].zfill(32)}
  通配符掩码: {bin(int(wildcard))[2:].zfill(32)}

【ACL配置示例】
  Cisco ACL:
    access-list 10 permit {mask_str.replace('0', 'x')}  {wildcard}
    
  Huawei ACL:
    rule permit ip source {mask_str.replace('0', 'x')}  {wildcard}

===========================================================
"""
            self.wildcard_result.delete("1.0", tk.END)
            self.wildcard_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"计算失败: {str(e)}")
            
    def create_ip_classification(self, parent):
        title = ttk.Label(parent, text="IP地址分类", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="查询IP地址的类别(A/B/C/D/E)、属性及特殊地址信息", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="输入IP地址", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row = ttk.Frame(input_frame)
        row.pack(fill=tk.X)
        
        ttk.Label(row, text="IP地址:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.classify_ip = ttk.Entry(row, width=20)
        self.classify_ip.insert(0, "172.16.0.1")
        self.classify_ip.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row, text="查询", command=self.classify_ip_address, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="分类结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.classify_result = scrolledtext.ScrolledText(result_frame, height=18, font=("Consolas", 10))
        self.classify_result.pack(fill=tk.BOTH, expand=True)
        
    def classify_ip_address(self):
        try:
            ip_str = self.classify_ip.get().strip()
            ip = ipaddress.ip_address(ip_str)
            first_octet = int(ip_str.split('.')[0])
            
            if first_octet < 128:
                ip_class = "A类"
                class_range = "1.0.0.0 - 126.255.255.255"
                default_mask = "255.0.0.0 (/8)"
                network_bits = 8
                host_bits = 24
                networks = 126
                hosts_per_network = 16777214
            elif first_octet < 192:
                ip_class = "B类"
                class_range = "128.0.0.0 - 191.255.255.255"
                default_mask = "255.255.0.0 (/16)"
                network_bits = 16
                host_bits = 16
                networks = 16384
                hosts_per_network = 65534
            elif first_octet < 224:
                ip_class = "C类"
                class_range = "192.0.0.0 - 223.255.255.255"
                default_mask = "255.255.255.0 (/24)"
                network_bits = 24
                host_bits = 8
                networks = 2097152
                hosts_per_network = 254
            elif first_octet < 240:
                ip_class = "D类 (组播)"
                class_range = "224.0.0.0 - 239.255.255.255"
                default_mask = "N/A"
                network_bits = "N/A"
                host_bits = "N/A"
                networks = "N/A"
                hosts_per_network = "N/A"
            else:
                ip_class = "E类 (保留)"
                class_range = "240.0.0.0 - 255.255.255.255"
                default_mask = "N/A"
                network_bits = "N/A"
                host_bits = "N/A"
                networks = "N/A"
                hosts_per_network = "N/A"
            
            special = []
            if ip.is_private: special.append("私有地址")
            if ip.is_loopback: special.append("环回地址")
            if ip.is_multicast: special.append("组播地址")
            if ip.is_link_local: special.append("链路本地地址")
            if ip.is_reserved: special.append("保留地址")
            if ip.is_global: special.append("全球单播地址")
            
            private_ranges = [
                "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
                "100.64.0.0/10 (CGN)", "169.254.0.0/16 (链路本地)", "127.0.0.0/8 (环回)"
            ]
            
            result = f"""
===========================================================
                IP地址分类查询
===========================================================

【IP地址】
  {ip_str}

【地址类别】
  类别:        {ip_class}
  地址范围:    {class_range}
  默认掩码:    {default_mask}
  网络位:      {network_bits}
  主机位:      {host_bits}
  网络数量:    {networks:,}
  每网络主机:  {hosts_per_network:,}

【地址属性】
  属性:        {', '.join(special) if special else '普通地址'}

【常见私有地址范围】
"""
            for pr in private_ranges:
                result += f"  {pr}\n"
            
            result += f"""
【特殊地址】
  0.0.0.0      - 默认路由/任意地址
  255.255.255.255 - 受限广播地址
  127.0.0.1    - 本地环回
  169.254.x.x  - APIPA (自动私有IP)
  224.0.0.1    - 所有主机组播
  224.0.0.2    - 所有路由器组播
  224.0.0.5    - OSPF路由器
  224.0.0.6    - OSPF DR/BDR
  224.0.0.9    - RIPv2路由器
  224.0.0.10   - EIGRP路由器
  224.0.0.18   - VRRP

===========================================================
"""
            self.classify_result.delete("1.0", tk.END)
            self.classify_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
            
    def create_vlan_calculator(self, parent):
        title = ttk.Label(parent, text="VLAN计算", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="查询VLAN ID信息、802.1Q标签结构、配置示例", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="VLAN信息", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row = ttk.Frame(input_frame)
        row.pack(fill=tk.X)
        
        ttk.Label(row, text="VLAN ID:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.vlan_id = ttk.Entry(row, width=10)
        self.vlan_id.insert(0, "10")
        self.vlan_id.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row, text="查询", command=self.query_vlan, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="VLAN信息", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.vlan_result = scrolledtext.ScrolledText(result_frame, height=15, font=("Consolas", 10))
        self.vlan_result.pack(fill=tk.BOTH, expand=True)
        
    def query_vlan(self):
        try:
            vlan_id = int(self.vlan_id.get())
            
            if vlan_id < 0 or vlan_id > 4095:
                messagebox.showerror("错误", "VLAN ID范围: 0-4095")
                return
            
            if vlan_id == 0:
                vlan_type = "保留 (Priority Tagged)"
                usage = "仅用于802.1Q优先级标记"
            elif vlan_id == 1:
                vlan_type = "默认VLAN"
                usage = "所有端口默认属于此VLAN，不可删除"
            elif 2 <= vlan_id <= 1001:
                vlan_type = "普通VLAN (Normal Range)"
                usage = "可创建、删除，存储在NVRAM"
            elif 1002 <= vlan_id <= 1005:
                vlan_type = "保留VLAN (FDDI/Token Ring)"
                usage = "自动创建，不可删除"
            elif 1006 <= vlan_id <= 4094:
                vlan_type = "扩展VLAN (Extended Range)"
                usage = "可创建，存储在running-config，部分功能受限"
            else:
                vlan_type = "保留"
                usage = "保留"
            
            vid_hex = hex(vlan_id)[2:].zfill(3)
            
            result = f"""
===========================================================
                VLAN信息查询
===========================================================

【VLAN ID】
  {vlan_id}

【VLAN类型】
  {vlan_type}

【用途说明】
  {usage}

【802.1Q标签信息】
  TPID (标签协议标识):  0x8100
  PCF (优先级代码字段): 0
  CFI (规范格式标识符): 0
  VID (VLAN标识符):     {vid_hex}

【配置示例】
  Cisco:
    vlan {vlan_id}
    name VLAN{vlan_id}
    
  Huawei:
    vlan {vlan_id}
    description VLAN{vlan_id}
    
  H3C:
    vlan {vlan_id}
    name VLAN{vlan_id}

【VLAN范围参考】
  0        - Priority Tagged
  1        - 默认VLAN
  2-1001   - 普通范围
  1002-1005 - FDDI/Token Ring保留
  1006-4094 - 扩展范围
  4095     - 保留

===========================================================
"""
            self.vlan_result.delete("1.0", tk.END)
            self.vlan_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
            
    def create_bandwidth_calculator(self, parent):
        title = ttk.Label(parent, text="带宽计算", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="计算文件传输时间，对比不同带宽下的传输速度", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="计算参数", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row = ttk.Frame(input_frame)
        row.pack(fill=tk.X)
        
        ttk.Label(row, text="文件大小:", width=10).pack(side=tk.LEFT, padx=(0, 5))
        self.file_size = ttk.Entry(row, width=12)
        self.file_size.insert(0, "1024")
        self.file_size.pack(side=tk.LEFT, padx=(0, 5))
        
        self.file_unit = ttk.Combobox(row, values=["MB", "GB", "TB", "KB"], width=6)
        self.file_unit.current(0)
        self.file_unit.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(row, text="带宽:", width=8).pack(side=tk.LEFT, padx=(0, 5))
        self.bandwidth = ttk.Entry(row, width=12)
        self.bandwidth.insert(0, "100")
        self.bandwidth.pack(side=tk.LEFT, padx=(0, 5))
        
        self.bandwidth_unit = ttk.Combobox(row, values=["Mbps", "Gbps", "Kbps"], width=6)
        self.bandwidth_unit.current(0)
        self.bandwidth_unit.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row, text="计算", command=self.calculate_bandwidth, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="计算结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.bandwidth_result = scrolledtext.ScrolledText(result_frame, height=15, font=("Consolas", 10))
        self.bandwidth_result.pack(fill=tk.BOTH, expand=True)
        
    def calculate_bandwidth(self):
        try:
            size = float(self.file_size.get())
            size_unit = self.file_unit.get()
            bw = float(self.bandwidth.get())
            bw_unit = self.bandwidth_unit.get()
            
            size_multipliers = {"KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
            file_bytes = size * size_multipliers[size_unit]
            file_bits = file_bytes * 8
            
            bw_multipliers = {"Kbps": 1000, "Mbps": 1000**2, "Gbps": 1000**3}
            bw_bps = bw * bw_multipliers[bw_unit]
            
            time_seconds = file_bits / bw_bps
            
            if time_seconds < 1:
                time_str = f"{time_seconds*1000:.2f} 毫秒"
            elif time_seconds < 60:
                time_str = f"{time_seconds:.2f} 秒"
            elif time_seconds < 3600:
                minutes = int(time_seconds // 60)
                seconds = time_seconds % 60
                time_str = f"{minutes} 分 {seconds:.1f} 秒"
            else:
                hours = int(time_seconds // 3600)
                minutes = int((time_seconds % 3600) // 60)
                seconds = time_seconds % 60
                time_str = f"{hours} 时 {minutes} 分 {seconds:.1f} 秒"
            
            common_bw = [
                ("10 Mbps", 10_000_000), ("100 Mbps", 100_000_000),
                ("1 Gbps", 1_000_000_000), ("10 Gbps", 10_000_000_000),
                ("40 Gbps", 40_000_000_000), ("100 Gbps", 100_000_000_000),
            ]
            
            result = f"""
===========================================================
                带宽/传输时间计算
===========================================================

【输入参数】
  文件大小:    {size} {size_unit} ({file_bytes:,} 字节)
  带宽:        {bw} {bw_unit} ({bw_bps:,} bps)

【传输时间】
  {time_str}

【不同带宽传输时间对比】
"""
            for name, bps in common_bw:
                t = file_bits / bps
                if t < 1: t_str = f"{t*1000:.0f} ms"
                elif t < 60: t_str = f"{t:.1f} s"
                elif t < 3600: t_str = f"{t/60:.1f} min"
                else: t_str = f"{t/3600:.2f} h"
                marker = " ← 当前" if bps == bw_bps else ""
                result += f"  {name:<12} {t_str:<15}{marker}\n"
            
            result += f"""
【单位换算参考】
  1 Byte = 8 bits    1 KB = 1,024 Bytes    1 MB = 1,024 KB
  1 GB = 1,024 MB    1 Kbps = 1,000 bps    1 Mbps = 1,000 Kbps

===========================================================
"""
            self.bandwidth_result.delete("1.0", tk.END)
            self.bandwidth_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"计算失败: {str(e)}")
            
    def create_port_lookup(self, parent):
        title = ttk.Label(parent, text="端口查询", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="查询端口号对应的服务名称、传输协议和说明", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="查询端口", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row = ttk.Frame(input_frame)
        row.pack(fill=tk.X)
        
        ttk.Label(row, text="端口号:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.port_number = ttk.Entry(row, width=10)
        self.port_number.insert(0, "80")
        self.port_number.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row, text="查询", command=self.lookup_port, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="端口信息", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.port_result = scrolledtext.ScrolledText(result_frame, height=18, font=("Consolas", 10))
        self.port_result.pack(fill=tk.BOTH, expand=True)
        
    def lookup_port(self):
        try:
            port = int(self.port_number.get())
            
            if port < 0 or port > 65535:
                messagebox.showerror("错误", "端口号范围: 0-65535")
                return
            
            if port < 1024:
                port_range = "知名端口 (Well-Known Ports)"
                range_desc = "0-1023，由IANA分配，需要管理员权限"
            elif port < 49152:
                port_range = "注册端口 (Registered Ports)"
                range_desc = "1024-49151，用于用户应用程序"
            else:
                port_range = "动态/私有端口 (Dynamic/Private Ports)"
                range_desc = "49152-65535，用于临时连接"
            
            common_ports = {
                20: ("FTP-Data", "TCP", "FTP数据传输"),
                21: ("FTP", "TCP", "FTP控制连接"),
                22: ("SSH", "TCP", "安全Shell"),
                23: ("Telnet", "TCP", "远程登录"),
                25: ("SMTP", "TCP", "简单邮件传输协议"),
                53: ("DNS", "TCP/UDP", "域名系统"),
                67: ("DHCP Server", "UDP", "DHCP服务器"),
                68: ("DHCP Client", "UDP", "DHCP客户端"),
                69: ("TFTP", "UDP", "简单文件传输协议"),
                80: ("HTTP", "TCP", "超文本传输协议"),
                110: ("POP3", "TCP", "邮局协议版本3"),
                123: ("NTP", "UDP", "网络时间协议"),
                143: ("IMAP", "TCP", "Internet邮件访问协议"),
                161: ("SNMP", "UDP", "简单网络管理协议"),
                162: ("SNMP Trap", "UDP", "SNMP陷阱"),
                443: ("HTTPS", "TCP", "HTTP over SSL/TLS"),
                445: ("SMB", "TCP", "服务器消息块"),
                514: ("Syslog", "UDP", "系统日志"),
                520: ("RIP", "UDP", "路由信息协议"),
                993: ("IMAPS", "TCP", "IMAP over SSL"),
                995: ("POP3S", "TCP", "POP3 over SSL"),
                1433: ("MSSQL", "TCP", "Microsoft SQL Server"),
                1521: ("Oracle", "TCP", "Oracle数据库"),
                1723: ("PPTP", "TCP", "点对点隧道协议"),
                1812: ("RADIUS Auth", "UDP", "RADIUS认证"),
                1813: ("RADIUS Acct", "UDP", "RADIUS计费"),
                3306: ("MySQL", "TCP", "MySQL数据库"),
                3389: ("RDP", "TCP", "远程桌面协议"),
                5432: ("PostgreSQL", "TCP", "PostgreSQL数据库"),
                5900: ("VNC", "TCP", "虚拟网络计算"),
                6379: ("Redis", "TCP", "Redis数据库"),
                8080: ("HTTP-Alt", "TCP", "HTTP备用端口"),
                8443: ("HTTPS-Alt", "TCP", "HTTPS备用端口"),
                27017: ("MongoDB", "TCP", "MongoDB数据库"),
            }
            
            service_info = common_ports.get(port, (None, None, None))
            
            result = f"""
===========================================================
                端口号查询
===========================================================

【端口号】
  {port}

【端口范围】
  {port_range}
  {range_desc}

"""
            if service_info[0]:
                result += f"""【服务信息】
  服务名称:    {service_info[0]}
  传输协议:    {service_info[1]}
  服务描述:    {service_info[2]}
"""
            else:
                result += "【服务信息】\n  未找到该端口的标准服务分配\n"
            
            result += f"""
【端口范围参考】
  0          - 保留
  1-1023     - 知名端口 (系统端口)
  1024-49151 - 注册端口 (用户端口)
  49152-65535 - 动态/私有端口 (临时端口)

【常见网络协议端口】
  20/21  - FTP          22   - SSH          23   - Telnet
  25     - SMTP         53   - DNS          67/68 - DHCP
  80     - HTTP         110  - POP3         123  - NTP
  161    - SNMP         443  - HTTPS        445  - SMB
  514    - Syslog       520  - RIP          1812 - RADIUS
  3306   - MySQL        3389 - RDP          5432 - PostgreSQL
  6379   - Redis        8080 - HTTP-Alt

===========================================================
"""
            self.port_result.delete("1.0", tk.END)
            self.port_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
            
    def create_mac_tools(self, parent):
        title = ttk.Label(parent, text="MAC地址工具", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="MAC地址格式转换、单播/组播判断、OUI查询", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="MAC地址", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row = ttk.Frame(input_frame)
        row.pack(fill=tk.X)
        
        ttk.Label(row, text="MAC地址:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.mac_address = ttk.Entry(row, width=20)
        self.mac_address.insert(0, "00:1A:2B:3C:4D:5E")
        self.mac_address.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row, text="查询", command=self.query_mac, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="MAC信息", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.mac_result = scrolledtext.ScrolledText(result_frame, height=15, font=("Consolas", 10))
        self.mac_result.pack(fill=tk.BOTH, expand=True)
        
    def query_mac(self):
        try:
            mac_str = self.mac_address.get().strip().replace('-', ':').replace('.', ':')
            
            parts = mac_str.split(':')
            if len(parts) != 6:
                messagebox.showerror("错误", "MAC地址格式错误")
                return
            
            mac_colon = ':'.join(f'{int(p, 16):02X}' for p in parts)
            mac_dash = '-'.join(f'{int(p, 16):02X}' for p in parts)
            mac_dot = '.'.join([
                f'{int(parts[0], 16):02X}{int(parts[1], 16):02X}',
                f'{int(parts[2], 16):02X}{int(parts[3], 16):02X}',
                f'{int(parts[4], 16):02X}{int(parts[5], 16):02X}'
            ])
            mac_no_sep = ''.join(f'{int(p, 16):02X}' for p in parts)
            
            first_byte = int(parts[0], 16)
            is_multicast = bool(first_byte & 0x01)
            is_universal = not bool(first_byte & 0x02)
            
            oui = ':'.join(parts[:3])
            
            result = f"""
===========================================================
                MAC地址信息
===========================================================

【MAC地址】
  {mac_colon}

【地址类型】
  单播/组播:   {'组播 (Multicast)' if is_multicast else '单播 (Unicast)'}
  全局/本地:   {'全局唯一 (UAA)' if is_universal else '本地管理 (LAA)'}

【OUI (组织唯一标识符)】
  {oui}

【不同格式表示】
  冒号分隔:    {mac_colon}
  横线分隔:    {mac_dash}
  点分格式:    {mac_dot} (Cisco格式)
  无分隔:      {mac_no_sep}
  二进制:      {bin(int(mac_no_sep, 16))[2:].zfill(48)}

【配置示例】
  Cisco 静态MAC:
    mac-address-table static {mac_colon} vlan 10 interface Gi0/1
    
  Huawei 静态MAC:
    mac-address static {mac_colon} GigabitEthernet 0/0/1 vlan 10

【MAC地址结构】
  |<--- 24 bits OUI --->|<--- 24 bits NIC --->|
  |  厂商代码 (前3字节)  |  设备序列号 (后3字节) |

【特殊MAC地址】
  00:00:00:00:00:00 - 空MAC
  FF:FF:FF:FF:FF:FF - 广播MAC
  01:00:5E:xx:xx:xx - IPv4组播MAC
  33:33:xx:xx:xx:xx - IPv6组播MAC

===========================================================
"""
            self.mac_result.delete("1.0", tk.END)
            self.mac_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
            
    def create_ospf_cost(self, parent):
        title = ttk.Label(parent, text="OSPF Cost", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="根据接口带宽和参考带宽计算OSPF Cost值", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="接口带宽", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row = ttk.Frame(input_frame)
        row.pack(fill=tk.X)
        
        ttk.Label(row, text="接口带宽:", width=10).pack(side=tk.LEFT, padx=(0, 5))
        self.ospf_bw = ttk.Entry(row, width=12)
        self.ospf_bw.insert(0, "100")
        self.ospf_bw.pack(side=tk.LEFT, padx=(0, 5))
        
        self.ospf_bw_unit = ttk.Combobox(row, values=["Mbps", "Gbps", "Kbps"], width=6)
        self.ospf_bw_unit.current(0)
        self.ospf_bw_unit.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(row, text="参考带宽:", width=10).pack(side=tk.LEFT, padx=(0, 5))
        self.ospf_ref = ttk.Entry(row, width=12)
        self.ospf_ref.insert(0, "100")
        self.ospf_ref.pack(side=tk.LEFT, padx=(0, 5))
        
        self.ospf_ref_unit = ttk.Combobox(row, values=["Mbps", "Gbps"], width=6)
        self.ospf_ref_unit.current(0)
        self.ospf_ref_unit.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row, text="计算", command=self.calculate_ospf_cost, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="OSPF Cost", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.ospf_result = scrolledtext.ScrolledText(result_frame, height=15, font=("Consolas", 10))
        self.ospf_result.pack(fill=tk.BOTH, expand=True)
        
    def calculate_ospf_cost(self):
        try:
            bw = float(self.ospf_bw.get())
            bw_unit = self.ospf_bw_unit.get()
            ref = float(self.ospf_ref.get())
            ref_unit = self.ospf_ref_unit.get()
            
            bw_multipliers = {"Kbps": 0.001, "Mbps": 1, "Gbps": 1000}
            bw_mbps = bw * bw_multipliers[bw_unit]
            ref_mbps = ref * bw_multipliers[ref_unit]
            
            cost = ref_mbps / bw_mbps
            if cost < 1: cost = 1
            cost = int(cost)
            
            interfaces = [
                ("10 Mbps Ethernet", 10), ("100 Mbps FastEthernet", 100),
                ("1 Gbps GigabitEthernet", 1000), ("10 Gbps TenGigabitEthernet", 10000),
                ("40 Gbps FortyGigE", 40000), ("100 Gbps HundredGigE", 100000),
                ("Serial T1 (1.544 Mbps)", 1.544), ("Serial E1 (2.048 Mbps)", 2.048),
            ]
            
            result = f"""
===========================================================
                OSPF Cost计算
===========================================================

【输入参数】
  接口带宽:    {bw} {bw_unit} ({bw_mbps} Mbps)
  参考带宽:    {ref} {ref_unit} ({ref_mbps} Mbps)

【OSPF Cost】
  Cost = {ref_mbps} / {bw_mbps} = {cost}

【常见接口OSPF Cost (参考带宽{ref_mbps}Mbps)】
"""
            for name, intf_bw in interfaces:
                c = int(ref_mbps / intf_bw) if ref_mbps / intf_bw >= 1 else 1
                marker = " ← 当前" if abs(intf_bw - bw_mbps) < 0.01 else ""
                result += f"  {name:<30} Cost: {c:<5}{marker}\n"
            
            result += f"""
【说明】
  OSPF Cost = 参考带宽 / 接口带宽
  默认参考带宽: 100 Mbps
  Cost最小值: 1    Cost最大值: 65535
  
  注意: 当接口带宽 >= 参考带宽时，Cost为1
  建议在高速网络中调大参考带宽

【配置命令】
  Cisco:
    router ospf 1
     auto-cost reference-bandwidth {int(ref_mbps)}
     
  Huawei:
    ospf 1
     bandwidth-reference {int(ref_mbps)}

===========================================================
"""
            self.ospf_result.delete("1.0", tk.END)
            self.ospf_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"计算失败: {str(e)}")
            
    def create_crc_calculator(self, parent):
        title = ttk.Label(parent, text="CRC校验", font=("Microsoft YaHei", 14, "bold"))
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(parent, text="计算CRC-8/CRC-16/CRC-32/FCS校验值", 
                        foreground="gray", font=("Microsoft YaHei", 9))
        desc.pack(pady=(0, 10))
        
        input_frame = ttk.LabelFrame(parent, text="输入数据", padding="15")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        row = ttk.Frame(input_frame)
        row.pack(fill=tk.X)
        
        ttk.Label(row, text="数据(十六进制):", width=15).pack(side=tk.LEFT, padx=(0, 5))
        self.crc_data = ttk.Entry(row, width=30)
        self.crc_data.insert(0, "01 02 03 04 05")
        self.crc_data.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(row, text="CRC类型:").pack(side=tk.LEFT, padx=(0, 5))
        self.crc_type = ttk.Combobox(row, values=["CRC-16", "CRC-32", "CRC-8", "FCS (Ethernet)"], width=15)
        self.crc_type.current(0)
        self.crc_type.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(row, text="计算", command=self.calculate_crc, width=10).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(parent, text="CRC结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.crc_result = scrolledtext.ScrolledText(result_frame, height=10, font=("Consolas", 10))
        self.crc_result.pack(fill=tk.BOTH, expand=True)
        
    def _crc16(self, data):
        crc = 0x0000
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x8005
                else:
                    crc = crc << 1
                crc &= 0xFFFF
        return crc
        
    def _crc32(self, data):
        return binascii.crc32(data) & 0xFFFFFFFF
        
    def _crc8(self, data):
        crc = 0x00
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x07
                else:
                    crc = crc << 1
                crc &= 0xFF
        return crc
        
    def calculate_crc(self):
        try:
            data_str = self.crc_data.get().strip().replace(' ', '')
            crc_type = self.crc_type.get()
            
            data_bytes = bytes.fromhex(data_str)
            
            if crc_type == "CRC-16":
                crc = self._crc16(data_bytes)
                crc_str = f"0x{crc:04X}"
                bits = 16
                poly = "0x8005"
            elif crc_type == "CRC-32":
                crc = self._crc32(data_bytes)
                crc_str = f"0x{crc:08X}"
                bits = 32
                poly = "0x04C11DB7"
            elif crc_type == "CRC-8":
                crc = self._crc8(data_bytes)
                crc_str = f"0x{crc:02X}"
                bits = 8
                poly = "0x07"
            else:  # FCS
                crc = self._crc32(data_bytes) ^ 0xFFFFFFFF
                crc_str = f"0x{crc:08X}"
                bits = 32
                poly = "0x04C11DB7"
            
            result = f"""
===========================================================
                CRC校验计算
===========================================================

【输入数据】
  {data_str}

【CRC类型】
  {crc_type}

【多项式】
  {poly}

【CRC结果】
  {crc_str}
  二进制: {bin(int(crc_str, 16))[2:].zfill(bits)}

【说明】
  CRC (Cyclic Redundancy Check) 循环冗余校验
  用于检测数据传输或存储过程中的错误
  
  CRC-8:   8位校验，用于简单校验
  CRC-16:  16位校验，用于Modbus等协议
  CRC-32:  32位校验，用于ZIP/PNG等
  FCS:     以太网帧校验序列

===========================================================
"""
            self.crc_result.delete("1.0", tk.END)
            self.crc_result.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"计算失败: {str(e)}")
            
    def open_ai_assistant(self):
        """打开AI协助窗口"""
        # 检查AI配置
        if self.main_app is None:
            messagebox.showwarning("提示", "AI协助功能需要主程序支持")
            return
            
        api_key = self.main_app.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("提示", "请先在AI智能配置页面设置API Key")
            return
            
        # 创建AI对话窗口
        dialog = tk.Toplevel(self.parent)
        dialog.title("AI网络助手")
        dialog.geometry("700x600")
        dialog.transient(self.parent)
        
        # 主容器
        main = ttk.Frame(dialog, padding="8")
        main.pack(fill=tk.BOTH, expand=True)
        
        # 说明
        info = ttk.Label(main, text="与AI对话解决网络问题，支持子网规划、路由配置、故障排查等",
                        foreground="gray", font=("Microsoft YaHei", 9))
        info.pack(fill=tk.X, pady=(0, 8))
        
        # 聊天记录
        chat_frame = ttk.LabelFrame(main, text="对话记录", padding="8")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        chat_text = scrolledtext.ScrolledText(chat_frame, height=20, font=("Consolas", 10), state=tk.DISABLED)
        chat_text.pack(fill=tk.BOTH, expand=True)
        chat_text.tag_config("user", foreground="#0066CC")
        chat_text.tag_config("ai", foreground="#009900")
        chat_text.tag_config("system", foreground="#999999")
        
        # 输入区域
        input_frame = ttk.Frame(main)
        input_frame.pack(fill=tk.X)
        
        input_text = scrolledtext.ScrolledText(input_frame, height=3, font=("Consolas", 10))
        input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        send_btn = ttk.Button(input_frame, text="发送", width=8)
        send_btn.pack(side=tk.TOP, fill=tk.Y)
        
        # 发送消息
        def send_message():
            msg = input_text.get("1.0", tk.END).strip()
            if not msg:
                return
                
            # 显示用户消息
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"\n[你] {msg}\n", "user")
            chat_text.insert(tk.END, "AI思考中...\n", "system")
            chat_text.see(tk.END)
            chat_text.config(state=tk.DISABLED)
            
            input_text.delete("1.0", tk.END)
            send_btn.config(state=tk.DISABLED)
            
            # 调用AI
            def ai_thread():
                try:
                    provider = self.main_app.ai_provider.get()
                    ai_model = self.main_app.ai_model.get()
                    
                    # 获取主界面选择的设备
                    vendor = self.main_app.vendor_combo.get()
                    device_model = self.main_app.model_combo.get()
                    device_display = f"{vendor} {device_model}"
                    device_type = self.main_app.get_selected_system_type()
                    
                    from ai_client import AIClient
                    ai = AIClient(provider, api_key, ai_model)
                    
                    prompt = f"""你是一个专业的网络工程师助手，精通各种网络设备配置和故障排查。

当前用户使用的设备: {device_display}
设备系统类型: {device_type}

当前用户正在使用网络计算工具，可能需要以下方面的帮助：
- 子网划分和IP地址规划
- VLAN配置和管理
- 路由协议（OSPF、BGP、EIGRP、静态路由）
- 交换机配置（STP、EtherChannel、端口安全）
- 网络安全（ACL、NAT、防火墙）
- 故障排查和诊断

请针对用户的问题，给出专业、准确、可操作的建议。
如果涉及配置命令，请针对{device_display}设备给出完整的命令示例。

用户问题：{msg}"""

                    result = ai.chat(prompt)
                    
                    self.parent.after(0, lambda: show_ai_response(result))
                except Exception as e:
                    self.parent.after(0, lambda: show_ai_error(str(e)))
                    
            def show_ai_response(response):
                chat_text.config(state=tk.NORMAL)
                # 删除"AI思考中..."
                chat_text.delete("end-2l linestart", "end-1l lineend")
                chat_text.insert(tk.END, f"\n[AI] {response}\n", "ai")
                chat_text.see(tk.END)
                chat_text.config(state=tk.DISABLED)
                send_btn.config(state=tk.NORMAL)
                
            def show_ai_error(error):
                chat_text.config(state=tk.NORMAL)
                chat_text.delete("end-2l linestart", "end-1l lineend")
                chat_text.insert(tk.END, f"\n[错误] {error}\n", "system")
                chat_text.see(tk.END)
                chat_text.config(state=tk.DISABLED)
                send_btn.config(state=tk.NORMAL)
                
            threading.Thread(target=ai_thread, daemon=True).start()
            
        send_btn.config(command=send_message)
        
        # 支持Enter发送
        def on_enter(event):
            if event.state & 0x4:  # Ctrl+Enter
                input_text.insert(tk.END, "\n")
            else:
                send_message()
                
        input_text.bind("<Return>", on_enter)
