import os
import json
import base64
import requests
from typing import List, Dict, Any, Optional
from .base_llm import BaseLLM

class DeepSeekClient(BaseLLM):
    """
    用于与DeepSeek API交互的客户端。
    """

    def __init__(self, model_name: str, api_key: str = None, base_url: str = "https://api.deepseek.com"):
        """
        初始化DeepSeek客户端。

        Args:
            model_name (str): 要使用的DeepSeek模型名称 (例如, 'deepseek-chat')。
            api_key (str, optional): API密钥。如果未提供，将从DEEPSEEK_API_KEY环境变量中读取。
            base_url (str): DeepSeek API的基本URL。
        """
        super().__init__(model_name)
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("未提供DeepSeek API密钥。请设置DEEPSEEK_API_KEY环境变量。")
        
        self.base_url = base_url
        self.api_url = f"{self.base_url}/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate(self, prompt: str, **kwargs) -> str:
        """
        从DeepSeek模型生成文本响应。
        """
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"调用DeepSeek API时出错: {e}")
            return f"错误: 无法连接到DeepSeek服务。{e}"
        except (KeyError, IndexError) as e:
            print(f"解析DeepSeek响应时出错: {e}")
            return f"错误: 响应格式不正确。{e}"

    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        使用工具调用生成响应。
        """
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools,
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            message = result["choices"][0]["message"]
            
            # 检查是否有工具调用
            if "tool_calls" in message:
                return {
                    "tool_calls": message["tool_calls"],
                    "content": message.get("content", "")
                }
            else:
                return {"text": message["content"]}
                
        except requests.exceptions.RequestException as e:
            print(f"调用DeepSeek API工具时出错: {e}")
            return {"error": f"无法连接到DeepSeek服务。{e}"}
        except (KeyError, IndexError) as e:
            print(f"解析DeepSeek工具响应时出错: {e}")
            return {"error": f"响应格式不正确。{e}"}

    def generate_vision(self, prompt: str, image_path: str, **kwargs) -> str:
        """
        使用DeepSeek视觉模型根据图像生成响应。
        注意：DeepSeek可能不支持视觉功能，这里提供一个基本实现。
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            return f"错误: 未找到图像文件: {image_path}"

        # 构造包含图像的消息
        image_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ]
        }

        payload = {
            "model": self.model_name,
            "messages": [image_message],
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"调用DeepSeek Vision API时出错: {e}")
            return f"错误: DeepSeek可能不支持视觉功能。{e}"
        except (KeyError, IndexError) as e:
            print(f"解析DeepSeek视觉响应时出错: {e}")
            return f"错误: 响应格式不正确。{e}" 