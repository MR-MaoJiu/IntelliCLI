import os
import base64
from typing import List, Dict, Any, Optional
from .base_llm import BaseLLM

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    anthropic = None
    Anthropic = None

class ClaudeClient(BaseLLM):
    """
    用于与Claude API交互的客户端。
    """

    def __init__(self, model_name: str, api_key: str = None):
        """
        初始化Claude客户端。

        Args:
            model_name (str): 要使用的Claude模型名称 (例如, 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307')。
            api_key (str, optional): API密钥。如果未提供，将从ANTHROPIC_API_KEY环境变量中读取。
        """
        if Anthropic is None:
            raise ImportError("需要安装anthropic库。请运行: pip install anthropic")
        
        super().__init__(model_name)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("未提供Claude API密钥。请设置ANTHROPIC_API_KEY环境变量。")
        
        self.client = Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, **kwargs) -> str:
        """
        从Claude模型生成文本响应。
        """
        # 设置默认参数
        message_kwargs = {
            "model": self.model_name,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "messages": [{"role": "user", "content": prompt}],
        }
        
        # 添加其他参数
        if "temperature" in kwargs:
            message_kwargs["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            message_kwargs["top_p"] = kwargs["top_p"]
        if "system" in kwargs:
            message_kwargs["system"] = kwargs["system"]
        
        try:
            response = self.client.messages.create(**message_kwargs)
            return response.content[0].text
        except Exception as e:
            print(f"调用Claude API时出错: {e}")
            return f"错误: {e}"

    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        使用工具调用生成响应。
        """
        message_kwargs = {
            "model": self.model_name,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools,
        }
        
        # 添加其他参数
        if "temperature" in kwargs:
            message_kwargs["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            message_kwargs["top_p"] = kwargs["top_p"]
        if "system" in kwargs:
            message_kwargs["system"] = kwargs["system"]
        
        try:
            response = self.client.messages.create(**message_kwargs)
            
            # 检查是否有工具调用
            tool_calls = []
            content = ""
            
            for content_block in response.content:
                if content_block.type == "text":
                    content += content_block.text
                elif content_block.type == "tool_use":
                    tool_calls.append({
                        "id": content_block.id,
                        "function": {
                            "name": content_block.name,
                            "arguments": content_block.input
                        }
                    })
            
            if tool_calls:
                return {
                    "tool_calls": tool_calls,
                    "content": content
                }
            else:
                return {"text": content}
                
        except Exception as e:
            print(f"调用Claude API工具时出错: {e}")
            return {"error": str(e)}

    def generate_vision(self, prompt: str, image_path: str, **kwargs) -> str:
        """
        使用Claude视觉模型根据图像生成响应。
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            return f"错误: 未找到图像文件: {image_path}"
        
        # 检测图像格式
        image_format = "image/jpeg"  # 默认
        if image_path.lower().endswith('.png'):
            image_format = "image/png"
        elif image_path.lower().endswith('.gif'):
            image_format = "image/gif"
        elif image_path.lower().endswith('.webp'):
            image_format = "image/webp"

        # 构造包含图像的消息
        image_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_format,
                        "data": encoded_image
                    }
                }
            ]
        }

        message_kwargs = {
            "model": self.model_name,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "messages": [image_message],
        }
        
        # 添加其他参数
        if "temperature" in kwargs:
            message_kwargs["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            message_kwargs["top_p"] = kwargs["top_p"]
        if "system" in kwargs:
            message_kwargs["system"] = kwargs["system"]
        
        try:
            response = self.client.messages.create(**message_kwargs)
            return response.content[0].text
        except Exception as e:
            print(f"调用Claude Vision API时出错: {e}")
            return f"错误: {e}" 