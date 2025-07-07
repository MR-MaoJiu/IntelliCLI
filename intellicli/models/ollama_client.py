import requests
import json
import base64
import os
from typing import List, Dict, Any, Optional
from .base_llm import BaseLLM

class OllamaClient(BaseLLM):
    """
    用于与本地或远程 Ollama 服务交互的客户端。
    """

    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        """
        初始化 Ollama 客户端。

        Args:
            model_name (str): 要使用的 Ollama 模型名称 (例如, 'llama3')。
            base_url (str): Ollama API 的基本 URL。
        """
        super().__init__(model_name)
        self.base_url = base_url
        self.api_url = f"{self.base_url}/api/generate"

    def generate(self, prompt: str, image_path: Optional[str] = None, **kwargs) -> str:
        """
        从 Ollama 模型生成文本响应。
        支持文本和图像输入。
        
        Args:
            prompt: 文本提示
            image_path: 可选的图像文件路径
            **kwargs: 其他生成选项
        """
        # 如果提供了图像路径，使用视觉生成功能
        if image_path and os.path.exists(image_path):
            return self.generate_vision(prompt, image_path, **kwargs)
        
        # 检查提示中是否包含图像引用
        if self._contains_image_reference(prompt):
            # 尝试从提示中提取图像路径
            extracted_path = self._extract_image_path(prompt)
            if extracted_path and os.path.exists(extracted_path):
                return self.generate_vision(prompt, extracted_path, **kwargs)
        
        # 标准文本生成
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,  # 我们希望一次性获得完整响应
            "options": kwargs
        }
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()  # 对不良状态码引发异常
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"连接到 Ollama 时出错: {e}")
            return "错误: 无法连接到 Ollama 服务。"
    
    def _contains_image_reference(self, prompt: str) -> bool:
        """检查提示中是否包含图像引用"""
        image_keywords = [
            "图像", "图片", "照片", "截图", "png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp",
            "image", "photo", "picture", "screenshot", "看图", "分析图", "识别图"
        ]
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in image_keywords)
    
    def _extract_image_path(self, prompt: str) -> Optional[str]:
        """从提示中提取图像路径"""
        import re
        
        # 匹配常见的文件路径模式
        path_patterns = [
            r'["\']([^"\']*\.(?:png|jpg|jpeg|gif|bmp|tiff|webp))["\']',  # 带引号的路径
            r'(\S+\.(?:png|jpg|jpeg|gif|bmp|tiff|webp))',  # 不带引号的路径
            r'文件路径[：:]\s*([^\s]+)',  # 中文文件路径标识
            r'image[:\s]+([^\s]+)',  # 英文图像路径标识
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                if os.path.exists(path):
                    return path
        
        return None

    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Ollama 不像其他一些 API 那样原生支持结构化工具调用。
        此实现将通过提示模型返回一个看起来像工具调用的 JSON 对象来模拟它。
        """
        # 这是一个简化的方法。更健壮的解决方案将涉及
        # 更复杂的提示工程，以确保模型返回有效的 JSON。
        tool_prompt = f"{prompt}\n\n可用工具: {json.dumps(tools)}\n\n如果您需要使用工具，请使用包含 'tool_call' 和 'arguments' 的 JSON 对象进行响应。"
        
        response_text = self.generate(tool_prompt, **kwargs)
        
        try:
            # 尝试将响应解析为工具调用
            response_json = json.loads(response_text)
            if "tool_call" in response_json:
                return response_json
        except json.JSONDecodeError:
            # 如果它不是有效的 JSON，则将其视为常规文本响应
            pass
            
        return {"text": response_text}

    def generate_vision(self, prompt: str, image_path: str, **kwargs) -> str:
        """
        使用多模态 Ollama 模型 (如 LLaVA) 根据图像生成响应。
        """
        # 注意: 这假设指定的模型 (例如, 'llava') 支持视觉。
        # 图像需要进行 base64 编码才能用于 API。
        import base64
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            return f"错误: 未找到图像文件: {image_path}"

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "images": [encoded_image]
        }
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"连接到 Ollama 时出错: {e}")
            return "错误: 无法连接到 Ollama 服务。"