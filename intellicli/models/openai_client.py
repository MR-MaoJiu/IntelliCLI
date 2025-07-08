import os
import base64
from typing import List, Dict, Any, Optional
from .base_llm import BaseLLM

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

class OpenAIClient(BaseLLM):
    """
    用于与OpenAI API交互的客户端。
    """

    def __init__(self, model_name: str, api_key: str = None, base_url: str = None):
        """
        初始化OpenAI客户端。

        Args:
            model_name (str): 要使用的OpenAI模型名称 (例如, 'gpt-4', 'gpt-3.5-turbo')。
            api_key (str, optional): API密钥。如果未提供，将从OPENAI_API_KEY环境变量中读取。
            base_url (str, optional): 自定义API基础URL，用于兼容OpenAI格式的其他服务。
        """
        if OpenAI is None:
            raise ImportError("需要安装openai库。请运行: pip install openai")
        
        super().__init__(model_name)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未提供OpenAI API密钥。请设置OPENAI_API_KEY环境变量。")
        
        # 初始化OpenAI客户端
        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = OpenAI(**client_kwargs)

    def generate(self, prompt: str, **kwargs) -> str:
        """
        从OpenAI模型生成文本响应。
        """
        # 设置默认参数
        chat_kwargs = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }
        
        try:
            response = self.client.chat.completions.create(**chat_kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用OpenAI API时出错: {e}")
            return f"错误: {e}"

    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        使用工具调用生成响应。
        """
        chat_kwargs = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools,
            **kwargs
        }
        
        try:
            response = self.client.chat.completions.create(**chat_kwargs)
            message = response.choices[0].message
            
            # 检查是否有工具调用
            if message.tool_calls:
                return {
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        } for tool_call in message.tool_calls
                    ],
                    "content": message.content
                }
            else:
                return {"text": message.content}
                
        except Exception as e:
            print(f"调用OpenAI API工具时出错: {e}")
            return {"error": str(e)}

    def generate_vision(self, prompt: str, image_path: str, **kwargs) -> str:
        """
        使用OpenAI视觉模型根据图像生成响应。
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            return f"错误: 未找到图像文件: {image_path}"
        
        # 检测图像格式
        image_format = "jpeg"  # 默认
        if image_path.lower().endswith('.png'):
            image_format = "png"
        elif image_path.lower().endswith('.gif'):
            image_format = "gif"
        elif image_path.lower().endswith('.webp'):
            image_format = "webp"

        # 构造包含图像的消息
        image_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{image_format};base64,{encoded_image}"
                    }
                }
            ]
        }

        # 确保使用支持视觉的模型
        vision_model = self.model_name
        if "gpt-4" not in vision_model.lower():
            vision_model = "gpt-4-vision-preview"  # 默认视觉模型

        chat_kwargs = {
            "model": vision_model,
            "messages": [image_message],
            "max_tokens": kwargs.get("max_tokens", 1000),
            **{k: v for k, v in kwargs.items() if k != "max_tokens"}
        }
        
        try:
            response = self.client.chat.completions.create(**chat_kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用OpenAI Vision API时出错: {e}")
            return f"错误: {e}"

# 为了向后兼容，也提供ChatGPTClient别名
class ChatGPTClient(OpenAIClient):
    """
    ChatGPT客户端，继承自OpenAIClient。
    """
    pass 