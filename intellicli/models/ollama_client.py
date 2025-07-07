import requests
import json
from typing import List, Dict, Any
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

    def generate(self, prompt: str, **kwargs) -> str:
        """
        从 Ollama 模型生成文本响应。
        """
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