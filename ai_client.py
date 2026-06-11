import json
import requests

class AIClient:
    """AI客户端，支持多种AI厂商API"""
    
    def __init__(self, provider, api_key, model):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_urls = {
            "OpenAI": "https://api.openai.com/v1/chat/completions",
            "Claude": "https://api.anthropic.com/v1/messages",
            "通义千问": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "文心一言": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
            "豆包": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            "DeepSeek": "https://api.deepseek.com/v1/chat/completions",
            "Qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "自定义API": ""
        }
        
    def generate_config(self, requirement, device_type):
        """
        根据需求生成配置命令
        返回: (命令列表, 解释说明)
        """
        system_prompt = self._get_system_prompt(device_type)
        user_prompt = self._get_user_prompt(requirement, device_type)
        
        if self.provider == "OpenAI":
            return self._call_openai(system_prompt, user_prompt)
        elif self.provider == "Claude":
            return self._call_claude(system_prompt, user_prompt)
        elif self.provider == "通义千问" or self.provider == "Qwen":
            return self._call_qwen(system_prompt, user_prompt)
        elif self.provider == "文心一言":
            return self._call_ernie(system_prompt, user_prompt)
        elif self.provider == "豆包":
            return self._call_doubao(system_prompt, user_prompt)
        elif self.provider == "DeepSeek":
            return self._call_deepseek(system_prompt, user_prompt)
        else:
            return self._call_custom_api(system_prompt, user_prompt)
            
    def _get_system_prompt(self, device_type):
        """获取系统提示词"""
        return f"""你是一个专业的网络设备配置专家，精通{device_type}系统的配置命令。

你的任务是：
1. 理解用户的配置需求
2. 生成正确的配置命令
3. 解释每条命令的作用

输出格式要求：
- 使用JSON格式返回
- 包含"commands"数组（配置命令列表）
- 包含"explanation"字符串（需求分析和命令解释）

示例输出格式：
{{
  "commands": ["command1", "command2", "command3"],
  "explanation": "需求分析：用户需要...\\n\\n命令解释：\\n1. command1 - 作用说明\\n2. command2 - 作用说明"
}}

注意事项：
- 只输出有效的{device_type}配置命令
- 命令应该是完整的，可以直接执行
- 不要包含注释符号（如!或#）在命令中
- 如果需要进入配置模式，包含相应的进入和退出命令
- 考虑安全性，避免破坏性操作"""

    def _get_user_prompt(self, requirement, device_type):
        """获取用户提示词"""
        return f"""设备类型：{device_type}

配置需求：
{requirement}

请根据上述需求，生成相应的配置命令。"""

    def _call_openai(self, system_prompt, user_prompt):
        """调用OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(
            self.base_urls["OpenAI"],
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return self._parse_response(content)
        else:
            raise Exception(f"OpenAI API错误: {response.status_code} - {response.text}")
            
    def _call_claude(self, system_prompt, user_prompt):
        """调用Claude API"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = requests.post(
            self.base_urls["Claude"],
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["content"][0]["text"]
            return self._parse_response(content)
        else:
            raise Exception(f"Claude API错误: {response.status_code} - {response.text}")
            
    def _call_qwen(self, system_prompt, user_prompt):
        """调用通义千问API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(
            self.base_urls["通义千问"],
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return self._parse_response(content)
        else:
            raise Exception(f"通义千问API错误: {response.status_code} - {response.text}")
            
    def _call_ernie(self, system_prompt, user_prompt):
        """调用文心一言API"""
        # 文心一言需要先获取access_token
        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        token_params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,  # API Key
            "client_secret": self.api_key  # 这里应该是Secret Key，简化处理
        }
        
        # 实际使用中需要分开API Key和Secret Key
        # 这里简化处理，假设用户传入的是access_token
        access_token = self.api_key
        
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.model}?access_token={access_token}"
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "messages": [
                {"role": "user", "content": system_prompt + "\n\n" + user_prompt}
            ],
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", "")
            return self._parse_response(content)
        else:
            raise Exception(f"文心一言API错误: {response.status_code} - {response.text}")
            
    def _call_doubao(self, system_prompt, user_prompt):
        """调用豆包API（兼容OpenAI格式）"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                self.base_urls["豆包"],
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return self._parse_response(content)
            else:
                raise Exception(f"豆包API错误: {response.status_code} - {response.text}")
        except requests.exceptions.Timeout:
            raise Exception("豆包API请求超时，请检查网络连接或稍后重试")
        except requests.exceptions.ConnectionError:
            raise Exception("豆包API连接失败，请检查网络设置")
            
    def _call_deepseek(self, system_prompt, user_prompt):
        """调用DeepSeek API（兼容OpenAI格式）"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                self.base_urls["DeepSeek"],
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return self._parse_response(content)
            else:
                raise Exception(f"DeepSeek API错误: {response.status_code} - {response.text}")
        except requests.exceptions.Timeout:
            raise Exception("DeepSeek API请求超时，请检查网络连接或稍后重试")
        except requests.exceptions.ConnectionError:
            raise Exception("DeepSeek API连接失败，请检查网络设置")
            
    def _call_custom_api(self, system_prompt, user_prompt):
        """调用自定义API"""
        # 这里提供一个通用的API调用模板
        # 用户可以根据自己的API格式修改
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        
        response = requests.post(
            "https://your-custom-api-endpoint/v1/chat/completions",  # 替换为实际API地址
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return self._parse_response(content)
        else:
            raise Exception(f"自定义API错误: {response.status_code} - {response.text}")
            
    def _parse_response(self, content):
        """解析AI返回的JSON响应"""
        try:
            # 尝试解析JSON
            result = json.loads(content)
            commands = result.get("commands", [])
            explanation = result.get("explanation", "无解释说明")
            return commands, explanation
        except json.JSONDecodeError:
            # 如果不是JSON格式，尝试从文本中提取命令
            return self._extract_commands_from_text(content)
            
    def _extract_commands_from_text(self, text):
        """从文本中提取命令（备用方案）"""
        commands = []
        explanation = text
        
        # 尝试提取代码块中的命令
        lines = text.split('\n')
        in_code_block = False
        current_commands = []
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if not in_code_block and current_commands:
                    commands.extend(current_commands)
                    current_commands = []
                continue
                
            if in_code_block:
                cmd = line.strip()
                if cmd and not cmd.startswith('#') and not cmd.startswith('!'):
                    current_commands.append(cmd)
                    
        if not commands:
            # 如果没有找到代码块，尝试提取每行
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('!') and not line.startswith('*'):
                    if len(line) < 100:  # 命令通常不会太长
                        commands.append(line)
                        
        return commands, explanation
        
    def chat(self, prompt):
        """通用聊天方法，返回纯文本（非JSON格式）"""
        if self.provider == "OpenAI":
            return self._chat_openai(prompt)
        elif self.provider == "Claude":
            return self._chat_claude(prompt)
        elif self.provider == "通义千问" or self.provider == "Qwen":
            return self._chat_qwen(prompt)
        elif self.provider == "文心一言":
            return self._chat_ernie(prompt)
        elif self.provider == "豆包":
            return self._chat_doubao(prompt)
        elif self.provider == "DeepSeek":
            return self._chat_deepseek(prompt)
        else:
            return self._chat_custom_api(prompt)
            
    def _chat_openai(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post(self.base_urls["OpenAI"], headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API错误: {response.status_code} - {response.text}")
            
    def _chat_claude(self, prompt):
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(self.base_urls["Claude"], headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            raise Exception(f"Claude API错误: {response.status_code} - {response.text}")
            
    def _chat_qwen(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post(self.base_urls["通义千问"], headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"通义千问API错误: {response.status_code} - {response.text}")
            
    def _chat_ernie(self, prompt):
        access_token = self.api_key
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.model}?access_token={access_token}"
        headers = {"Content-Type": "application/json"}
        data = {"messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json().get("result", "")
        else:
            raise Exception(f"文心一言API错误: {response.status_code} - {response.text}")
            
    def _chat_doubao(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post(self.base_urls["豆包"], headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"豆包API错误: {response.status_code} - {response.text}")
            
    def _chat_deepseek(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post(self.base_urls["DeepSeek"], headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"DeepSeek API错误: {response.status_code} - {response.text}")
            
    def _chat_custom_api(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post("https://your-custom-api-endpoint/v1/chat/completions", headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"自定义API错误: {response.status_code} - {response.text}")
