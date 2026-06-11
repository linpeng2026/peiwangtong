import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import json
import os
import sys
from datetime import datetime
from network_device import NetworkDevice
from ai_client import AIClient
from network_tools import NetworkToolsPage
from ops_tools import OpsToolsPage
from device_models import get_vendors, get_types, get_models, get_system_type


def get_base_dir():
    """获取程序所在目录（兼容 PyInstaller 打包）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

class NetworkConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("企业级交换路由自动配置系统")
        self.root.geometry("1200x800")
        
        # 初始化组件
        self.ai_client = None
        self.pending_commands = []
        self.config_history = []
        self.generating = False
        self.history_file = os.path.join(get_base_dir(), "command_history.json")
        self.load_history()
        
        # 创建界面
        self.create_widgets()
        self.load_config()
        self._refresh_history_list()
        
    def create_widgets(self):
        # 设置窗口图标和样式
        self.root.title("配网通 - 企业级交换路由自动配置系统")
        self.root.geometry("1400x900")
        
        # 创建主笔记本（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # === 标签页1: AI智能配置 ===
        config_tab = ttk.Frame(self.notebook)
        self.notebook.add(config_tab, text="  AI智能配置  ")
        
        # 创建主框架 - 左右分栏布局
        main_frame = ttk.Frame(config_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板（连接+AI配置）
        left_panel = ttk.Frame(main_frame, width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # 右侧面板（输出+历史）
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # ===== 左侧面板 =====
        
        # 设备选择区域（厂商 → 类型 → 型号）
        dev_frame = ttk.LabelFrame(left_panel, text=" 设备信息 ", padding="10")
        dev_frame.pack(fill=tk.X, pady=(0, 8))
        
        # 第一行：厂商 + 类型
        row1 = ttk.Frame(dev_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1, text="厂商:").pack(side=tk.LEFT, padx=(0, 3))
        self.vendor_combo = ttk.Combobox(row1, width=18)
        self.vendor_combo['values'] = get_vendors()
        self.vendor_combo.current(0)
        self.vendor_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.vendor_combo.bind("<<ComboboxSelected>>", self.on_vendor_change)
        
        ttk.Label(row1, text="类型:").pack(side=tk.LEFT, padx=(0, 3))
        self.type_combo = ttk.Combobox(row1, width=18)
        self.type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.type_combo.bind("<<ComboboxSelected>>", self.on_type_change)
        
        # 第二行：型号（独占一行，宽度拉满）
        row2 = ttk.Frame(dev_frame)
        row2.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row2, text="型号:").pack(side=tk.LEFT, padx=(0, 3))
        self.model_combo = ttk.Combobox(row2, width=50)
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 初始化设备列表
        self.on_vendor_change()
        
        # AI配置区域
        ai_frame = ttk.LabelFrame(left_panel, text=" AI配置 ", padding="10")
        ai_frame.pack(fill=tk.X, pady=(0, 8))
        
        # AI厂商 + API Key
        ai_row1 = ttk.Frame(ai_frame)
        ai_row1.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(ai_row1, text="厂商:").pack(side=tk.LEFT, padx=(0, 3))
        self.ai_provider = ttk.Combobox(ai_row1, values=["OpenAI", "Claude", "通义千问", "文心一言", "豆包", "DeepSeek", "Qwen", "自定义API"], width=12)
        self.ai_provider.current(0)
        self.ai_provider.pack(side=tk.LEFT, padx=(0, 8))
        self.ai_provider.bind("<<ComboboxSelected>>", self.on_ai_provider_change)
        
        ttk.Label(ai_row1, text="Key:").pack(side=tk.LEFT, padx=(0, 3))
        self.api_key_entry = ttk.Entry(ai_row1, width=18, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_ai_config_btn = ttk.Button(ai_row1, text="保存", command=self.save_ai_config)
        self.save_ai_config_btn.pack(side=tk.RIGHT, padx=(0, 3))
        
        self.clear_ai_config_btn = ttk.Button(ai_row1, text="清除", command=self.clear_ai_config)
        self.clear_ai_config_btn.pack(side=tk.RIGHT)
        
        # 模型选择
        ai_row2 = ttk.Frame(ai_frame)
        ai_row2.pack(fill=tk.X)
        
        ttk.Label(ai_row2, text="模型:").pack(side=tk.LEFT, padx=(0, 3))
        self.ai_model = ttk.Combobox(ai_row2, values=["gpt-4", "gpt-3.5-turbo", "claude-3", "qwen-max", "ernie-bot"], width=20)
        self.ai_model.current(0)
        self.ai_model.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 需求输入区域
        req_frame = ttk.LabelFrame(left_panel, text=" 配置需求 ", padding="10")
        req_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        self.requirement_text = scrolledtext.ScrolledText(req_frame, height=8, font=("Microsoft YaHei", 10))
        self.requirement_text.pack(fill=tk.BOTH, expand=True)
        
        # 操作按钮
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.generate_btn = ttk.Button(btn_frame, text="生成命令", command=self.generate_config)
        self.generate_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        
        self.stop_generate_btn = ttk.Button(btn_frame, text="停止", command=self.stop_generate, state=tk.DISABLED)
        self.stop_generate_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        
        ttk.Button(btn_frame, text="清空", command=self.clear_output).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ===== 右侧面板 =====
        
        # 命令输出区域
        cmd_frame = ttk.LabelFrame(right_panel, text=" 命令输出 ", padding="8")
        cmd_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(cmd_frame, height=20, font=("Consolas", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置文本标签用于高亮
        self.output_text.tag_config("command", foreground="#0066CC")
        self.output_text.tag_config("success", foreground="#009900")
        self.output_text.tag_config("error", foreground="#CC0000")
        self.output_text.tag_config("info", foreground="#666666")
        self.output_text.tag_config("ai_response", foreground="#9933CC")
        
        # 配置历史区域
        history_frame = ttk.LabelFrame(right_panel, text=" 配置历史 ", padding="8")
        history_frame.pack(fill=tk.X)
        
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.history_listbox = tk.Listbox(history_frame, height=5, font=("Microsoft YaHei", 9))
        self.history_listbox.pack(fill=tk.X)
        self.history_listbox.bind("<Double-Button-1>", self.restore_history)
        
        # 历史操作按钮
        hist_btn_frame = ttk.Frame(history_frame)
        hist_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(hist_btn_frame, text="恢复选中", command=self.restore_history).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(hist_btn_frame, text="清空历史", command=self.clear_history).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Label(status_bar, textvariable=self.status_var, anchor=tk.W, padding=(10, 3)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(status_bar, text="配网通 V1.0 | 制作人：林鹏 | Copyright (C) 2026", anchor=tk.E, padding=(10, 3), foreground="#888888").pack(side=tk.RIGHT)
        
        # === 标签页2: AI结果分析 ===
        analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(analysis_tab, text="  AI结果分析  ")
        self.create_analysis_tab(analysis_tab)
        
        # === 标签页3: 网络计算工具 ===
        tools_tab = ttk.Frame(self.notebook)
        self.notebook.add(tools_tab, text="  网络计算工具  ")
        self.network_tools = NetworkToolsPage(tools_tab, main_app=self)
        
        # === 标签页4: 网络运维工具 ===
        ops_tab = ttk.Frame(self.notebook)
        self.notebook.add(ops_tab, text="  网络运维工具  ")
        self.ops_tools = OpsToolsPage(ops_tab, main_app=self)
        
    def get_selected_system_type(self):
        """获取当前选中设备的系统类型"""
        model = self.model_combo.get()
        return get_system_type(model)
        
    def on_vendor_change(self, event=None):
        """厂商改变时更新类型列表"""
        vendor = self.vendor_combo.get()
        types = get_types(vendor)
        self.type_combo['values'] = types
        if types:
            self.type_combo.current(0)
            self.on_type_change()
            
    def on_type_change(self, event=None):
        """类型改变时更新型号列表"""
        vendor = self.vendor_combo.get()
        device_type = self.type_combo.get()
        models = get_models(vendor, device_type)
        self.model_combo['values'] = models
        if models:
            self.model_combo.current(0)
        
    def on_ai_provider_change(self, event=None):
        """AI厂商切换时更新模型选项"""
        provider = self.ai_provider.get()
        models = {
            "OpenAI": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            "Claude": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "通义千问": ["qwen-max", "qwen-plus", "qwen-turbo"],
            "文心一言": ["ernie-bot", "ernie-bot-turbo", "ernie-bot-4"],
            "豆包": ["doubao-pro-32k", "doubao-lite-32k", "doubao-pro-128k"],
            "DeepSeek": ["deepseek-v4-flash"],
            "Qwen": ["qwen-max", "qwen-plus", "qwen-turbo", "qwen-long"],
            "自定义API": ["custom-model"]
        }
        self.ai_model['values'] = models.get(provider, ["gpt-4"])
        if self.ai_model['values']:
            self.ai_model.current(0)
            
    def generate_config(self):
        """使用AI生成配置命令"""
        requirement = self.requirement_text.get("1.0", tk.END).strip()
        if not requirement:
            messagebox.showwarning("警告", "请输入配置需求")
            return
            
        if not self.ai_client:
            self.init_ai_client()
            
        if not self.ai_client:
            messagebox.showerror("错误", "AI客户端未正确初始化，请检查API配置")
            return
            
        self.status_var.set("AI正在生成配置命令...")
        self.generate_btn.config(state=tk.DISABLED)
        self.stop_generate_btn.config(state=tk.NORMAL)
        self.generating = True
        
        # 在后台线程中调用AI
        def generate_thread():
            try:
                device_type = self.get_selected_system_type()
                commands, explanation = self.ai_client.generate_config(
                    requirement, device_type
                )
                
                if not self.generating:
                    self.root.after(0, lambda: self.on_generate_stopped())
                    return
                
                self.root.after(0, lambda: self.on_generate_complete(commands, explanation))
            except Exception as e:
                err_msg = str(e)
                self.root.after(0, lambda msg=err_msg: self.on_generate_error(msg))
                
        threading.Thread(target=generate_thread, daemon=True).start()
        
    def on_generate_complete(self, commands, explanation):
        """生成配置完成回调"""
        self.generate_btn.config(state=tk.NORMAL)
        self.stop_generate_btn.config(state=tk.DISABLED)
        self.generating = False
        self.status_var.set("配置命令生成完成")
        
        self.log_output("\n" + "="*50, "info")
        self.log_output("[AI] 配置需求分析:", "ai_response")
        self.log_output(explanation, "ai_response")
        self.log_output("\n[AI] 生成的配置命令:", "ai_response")
        
        for cmd in commands:
            self.log_output(f"  {cmd}", "command")
            
        self.log_output("="*50 + "\n", "info")
        
        # 保存生成的命令供执行使用
        self.pending_commands = commands
        
        # 保存到历史
        self._save_to_history(self.output_text.get("1.0", tk.END).strip(), commands[:])
        
    def on_generate_error(self, error_msg):
        """生成配置错误回调"""
        self.generate_btn.config(state=tk.NORMAL)
        self.stop_generate_btn.config(state=tk.DISABLED)
        self.generating = False
        self.status_var.set(f"生成失败: {error_msg}")
        self.log_output(f"[ERROR] AI生成配置失败: {error_msg}", "error")

    def stop_generate(self):
        """停止生成命令"""
        self.generating = False
        self.generate_btn.config(state=tk.NORMAL)
        self.stop_generate_btn.config(state=tk.DISABLED)
        self.status_var.set("已停止生成")
        self.log_output("\n[INFO] 用户已停止生成命令", "info")

    def on_generate_stopped(self):
        """生成被停止回调"""
        self.generate_btn.config(state=tk.NORMAL)
        self.stop_generate_btn.config(state=tk.DISABLED)
        self.generating = False
        self.status_var.set("已停止生成")
        
    def init_ai_client(self):
        """初始化AI客户端"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入API Key")
            return
            
        provider = self.ai_provider.get()
        model = self.ai_model.get()
        
        try:
            self.ai_client = AIClient(provider, api_key, model)
            self.log_output(f"[INFO] AI客户端初始化成功 ({provider} - {model})", "info")
        except Exception as e:
            self.log_output(f"[ERROR] AI客户端初始化失败: {str(e)}", "error")
            
    def save_ai_config(self):
        """保存AI配置到本地"""
        config = {
            "ai_provider": self.ai_provider.get(),
            "api_key": self.api_key_entry.get(),
            "ai_model": self.ai_model.get()
        }
        
        config_path = os.path.join(get_base_dir(), "ai_config.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", "AI配置已保存")
            self.log_output("[INFO] AI配置已保存到本地", "info")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            
    def clear_ai_config(self):
        """清除保存的AI配置"""
        config_path = os.path.join(get_base_dir(), "ai_config.json")
        if os.path.exists(config_path):
            try:
                os.remove(config_path)
                self.api_key_entry.delete(0, tk.END)
                self.ai_provider.set("OpenAI")
                self.ai_model.set("gpt-4")
                self.on_ai_provider_change()
                messagebox.showinfo("成功", "AI配置已清除")
                self.log_output("[INFO] AI配置已清除", "info")
            except Exception as e:
                messagebox.showerror("错误", f"清除配置失败: {str(e)}")
        else:
            messagebox.showinfo("提示", "没有保存的AI配置")
            
    def load_config(self):
        """加载本地配置"""
        # 加载AI配置
        config_path = os.path.join(get_base_dir(), "ai_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.ai_provider.set(config.get("ai_provider", "OpenAI"))
                self.api_key_entry.insert(0, config.get("api_key", ""))
                self.ai_model.set(config.get("ai_model", "gpt-4"))
                self.on_ai_provider_change()
            except Exception as e:
                print(f"加载AI配置失败: {e}")
                
    def log_output(self, message, tag="info"):
        """输出日志到文本框"""
        self.output_text.insert(tk.END, message + "\n", tag)
        self.output_text.see(tk.END)
        
    def clear_output(self):
        """清空输出并保存到历史"""
        # 保存当前输出到历史
        content = self.output_text.get("1.0", tk.END).strip()
        if content and hasattr(self, 'pending_commands') and self.pending_commands:
            self._save_to_history(content, self.pending_commands[:])
        
        self.output_text.delete("1.0", tk.END)
        self.pending_commands = []
        
    def _save_to_history(self, output, commands):
        """保存配置到历史文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        requirement = self.requirement_text.get("1.0", tk.END).strip()
        
        history_item = {
            "id": len(self.config_history) + 1,
            "timestamp": timestamp,
            "requirement": requirement,
            "commands": commands,
            "output": output
        }
        
        self.config_history.append(history_item)
        self._persist_history()
        self._refresh_history_list()
        
    def _persist_history(self):
        """持久化历史到文件"""
        try:
            # 只保留最近50条
            recent = self.config_history[-50:]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(recent, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")
            
    def load_history(self):
        """从文件加载历史"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.config_history = json.load(f)
            except Exception as e:
                self.config_history = []
                
    def _refresh_history_list(self):
        """刷新历史列表显示"""
        self.history_listbox.delete(0, tk.END)
        for item in reversed(self.config_history):
            display = f"[{item['timestamp']}] {item['requirement'][:40]}..."
            self.history_listbox.insert(tk.END, display)
            
    def restore_history(self, event=None):
        """从历史恢复配置"""
        sel = self.history_listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一条历史记录")
            return
            
        # 列表是倒序显示的，需要转换索引
        idx = len(self.config_history) - 1 - sel[0]
        if idx < 0 or idx >= len(self.config_history):
            return
            
        item = self.config_history[idx]
        
        # 清空输出并恢复
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", item["output"])
        
        # 恢复需求
        self.requirement_text.delete("1.0", tk.END)
        self.requirement_text.insert("1.0", item["requirement"])
        
        # 恢复命令
        self.pending_commands = item.get("commands", [])
        
        self.status_var.set(f"已恢复历史配置: {item['timestamp']}")
        self.log_output(f"\n[历史恢复] {item['timestamp']}", "info")
        
    def clear_history(self):
        """清空历史记录"""
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
            self.config_history = []
            self._persist_history()
            self._refresh_history_list()
            self.status_var.set("历史记录已清空")
            
    def create_analysis_tab(self, parent):
        """创建AI结果分析标签页"""
        # 左右分栏
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # 左侧：输入区域
        left_panel = ttk.Frame(main_frame, width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # 右侧：分析结果
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # === 左侧 ===
        
        # 说明
        info_frame = ttk.LabelFrame(left_panel, text="使用说明", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 8))
        
        info_text = "将设备返回的命令输出（成功/失败/报错等）粘贴到下方，AI将自动分析结果并给出建议。\n\nAI配置和设备类型使用主界面的统一配置。"
        ttk.Label(info_frame, text=info_text, wraplength=420, foreground="gray").pack()
        
        # 设备输出输入
        input_frame = ttk.LabelFrame(left_panel, text="设备返回结果", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        self.analysis_input = scrolledtext.ScrolledText(input_frame, height=12, font=("Consolas", 10))
        self.analysis_input.pack(fill=tk.BOTH, expand=True)
        
        # 操作按钮
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.analysis_btn = ttk.Button(btn_frame, text="AI分析", command=self.analyze_output)
        self.analysis_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        
        ttk.Button(btn_frame, text="清空", command=self.clear_analysis).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === 右侧 ===
        
        result_frame = ttk.LabelFrame(right_panel, text="分析结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.analysis_result = scrolledtext.ScrolledText(result_frame, height=30, font=("Consolas", 10))
        self.analysis_result.pack(fill=tk.BOTH, expand=True)
        
        self.analysis_result.tag_config("success", foreground="#009900")
        self.analysis_result.tag_config("error", foreground="#CC0000")
        self.analysis_result.tag_config("warning", foreground="#FF9900")
        self.analysis_result.tag_config("info", foreground="#0066CC")
        
    def analyze_output(self):
        """使用AI分析设备返回结果"""
        device_output = self.analysis_input.get("1.0", tk.END).strip()
        if not device_output:
            messagebox.showwarning("警告", "请粘贴设备返回的结果")
            return
            
        # 使用主界面的统一AI配置和设备
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请先在主界面配置AI API Key")
            return
            
        provider = self.ai_provider.get()
        model = self.ai_model.get()
        device_type = self.get_selected_system_type()
        
        self.status_var.set("AI正在分析设备返回结果...")
        self.analysis_btn.config(state=tk.DISABLED)
        self.analysis_result.delete("1.0", tk.END)
        self.analysis_result.insert("1.0", "正在分析中，请稍候...\n", "info")
        
        def analyze_thread():
            try:
                ai = AIClient(provider, api_key, model)
                
                prompt = f"""你是一个专业的网络设备工程师。请分析以下{device_type}设备返回的命令结果，并给出详细分析：

【设备类型】{device_type}

【设备返回结果】
{device_output}

请从以下几个方面进行分析：
1. 【执行状态】命令是否执行成功？是否有报错？
2. 【错误分析】如果有错误，错误原因是什么？
3. 【配置影响】这些输出对设备配置有什么影响？
4. 【建议方案】如果有问题，如何解决？给出具体建议。
5. 【注意事项】需要特别注意的事项。

请用简洁明了的中文回答。"""

                result = ai.chat(prompt)
                
                self.root.after(0, lambda: self.on_analyze_complete(result))
            except Exception as e:
                self.root.after(0, lambda: self.on_analyze_error(str(e)))
                
        threading.Thread(target=analyze_thread, daemon=True).start()
        
    def on_analyze_complete(self, result):
        """分析完成回调"""
        self.analysis_btn.config(state=tk.NORMAL)
        self.status_var.set("AI分析完成")
        
        self.analysis_result.delete("1.0", tk.END)
        
        # 简单关键词高亮
        lines = result.split('\n')
        for line in lines:
            if any(kw in line for kw in ["成功", "正常", "正确", "无错误", "无问题"]):
                self.analysis_result.insert(tk.END, line + "\n", "success")
            elif any(kw in line for kw in ["失败", "错误", "报错", "异常", "问题"]):
                self.analysis_result.insert(tk.END, line + "\n", "error")
            elif any(kw in line for kw in ["注意", "警告", "建议", "谨慎"]):
                self.analysis_result.insert(tk.END, line + "\n", "warning")
            else:
                self.analysis_result.insert(tk.END, line + "\n")
                
    def on_analyze_error(self, error_msg):
        """分析错误回调"""
        self.analysis_btn.config(state=tk.NORMAL)
        self.status_var.set(f"分析失败: {error_msg}")
        self.analysis_result.delete("1.0", tk.END)
        self.analysis_result.insert("1.0", f"分析失败: {error_msg}", "error")
        
    def clear_analysis(self):
        """清空分析"""
        self.analysis_input.delete("1.0", tk.END)
        self.analysis_result.delete("1.0", tk.END)

def main():
    root = tk.Tk()
    app = NetworkConfigApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
