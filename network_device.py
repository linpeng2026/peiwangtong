import paramiko
import time
import re

class NetworkDevice:
    """网络设备连接和操作类"""
    
    def __init__(self, ip, port, username, password, device_type):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.device_type = device_type
        self.ssh_client = None
        self.channel = None
        self.connected = False
        
    def connect(self):
        """连接设备"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=self.ip,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
                allow_agent=False,
                look_for_keys=False
            )
            
            self.channel = self.ssh_client.invoke_shell()
            time.sleep(2)  # 等待shell初始化
            
            # 清除初始输出
            if self.channel.recv_ready():
                self.channel.recv(65535)
                
            self.connected = True
            return True, "连接成功"
            
        except paramiko.AuthenticationException:
            return False, "认证失败，请检查用户名和密码"
        except paramiko.SSHException as e:
            return False, f"SSH连接错误: {str(e)}"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
            
    def disconnect(self):
        """断开连接"""
        try:
            if self.channel:
                self.channel.close()
            if self.ssh_client:
                self.ssh_client.close()
            self.connected = False
        except:
            pass
            
    def execute_command(self, command):
        """执行命令"""
        if not self.connected:
            return False, "设备未连接"
            
        try:
            # 发送命令
            self.channel.send(command + "\n")
            time.sleep(1)  # 等待命令执行
            
            # 接收输出
            output = ""
            timeout = time.time() + 10  # 10秒超时
            
            while time.time() < timeout:
                if self.channel.recv_ready():
                    chunk = self.channel.recv(65535).decode('utf-8', errors='ignore')
                    output += chunk
                    # 检查是否回到提示符
                    if self._is_prompt(output):
                        break
                time.sleep(0.1)
                
            return True, output.strip()
            
        except Exception as e:
            return False, f"命令执行失败: {str(e)}"
            
    def _is_prompt(self, output):
        """检查是否回到命令提示符"""
        lines = output.strip().split('\n')
        if not lines:
            return False
            
        last_line = lines[-1].strip()
        
        # 不同设备的提示符模式
        patterns = [
            r'.*>$',           # Cisco user mode
            r'.*#$',           # Cisco enable mode / Linux
            r'.*>$',           # Huawei/H3C user mode
            r'.*]$',           # Huawei/H3C system view
            r'.*#$',           # Juniper
            r'.*\(config.*\)#$' # Cisco config mode
        ]
        
        for pattern in patterns:
            if re.match(pattern, last_line):
                return True
                
        return False
        
    def send_command_list(self, commands, delay=0.5):
        """批量发送命令"""
        results = []
        for cmd in commands:
            success, output = self.execute_command(cmd)
            results.append((cmd, success, output))
            time.sleep(delay)
        return results
